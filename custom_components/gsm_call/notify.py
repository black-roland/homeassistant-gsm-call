# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import asyncio
import logging
import re

import homeassistant.helpers.config_validation as cv
import serial
import voluptuous as vol
from homeassistant.components.notify import (
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_AT_COMMAND = "at_command"
CONF_CALL_DURATION_SEC = "call_duration_sec"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE): cv.isdevice,
        vol.Required(CONF_AT_COMMAND, default="ATD"): cv.matches_regex("^(ATD|ATDT)$"),
        vol.Required(CONF_CALL_DURATION_SEC, default=25): cv.positive_int,
    }
)


def get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> GsmCallNotificationService:
    return GsmCallNotificationService(
        config[CONF_DEVICE],
        config[CONF_AT_COMMAND],
        config[CONF_CALL_DURATION_SEC],
    )


class GsmCallNotificationService(BaseNotificationService):
    modem: serial.Serial = None

    def __init__(self, device_path, at_command, call_duration):
        self.device_path = device_path
        self.at_command = at_command
        self.call_duration = call_duration

    async def async_send_message(self, message="", **kwargs):
        if not (targets := kwargs.get(ATTR_TARGET)):
            _LOGGER.info("At least 1 target is required")
            return

        for target in targets:
            try:
                phone_number_re = re.compile(r"^\+?[1-9]\d{1,14}$")
                if not phone_number_re.match(target):
                    raise Exception("Invalid phone number")
                phone_number = re.sub(r"\D", "", target)

                await self._async_dial_target(phone_number)
            except Exception as ex:
                _LOGGER.exception(ex)

    def connect(self):
        GsmCallNotificationService.modem = serial.Serial(
            self.device_path,
            baudrate=75600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=5,
            dsrdtr=True,
            rtscts=True,
        )

    def terminate(self):
        GsmCallNotificationService.modem.close()
        GsmCallNotificationService.modem = None

    async def _async_dial_target(self, phone_number):
        if GsmCallNotificationService.modem:
            raise Exception("Already making a voice call")

        _LOGGER.info(f"Connecting to {self.device_path}...")
        self.connect()

        GsmCallNotificationService.modem.write(b"AT\r\n")
        _LOGGER.debug("AT sent")

        try:
            await asyncio.wait_for(self.hass.async_add_executor_job(GsmCallNotificationService.modem.read_until, b"OK"), 5)
            _LOGGER.info("Connection established")
        except TimeoutError:
            self.terminate()
            raise Exception("Timed out waiting for connection")

        _LOGGER.debug(f"Dialing +{phone_number}...")
        GsmCallNotificationService.modem.write(f"{self.at_command}+{phone_number};\r\n".encode())

        try:
            done, pending = await asyncio.wait(
                [
                    self.hass.async_add_executor_job(GsmCallNotificationService.modem.read_until, b"OK"),
                    self.hass.async_add_executor_job(GsmCallNotificationService.modem.read_until, b"ERROR"),
                ],
                return_when=asyncio.FIRST_COMPLETED,
                timeout=5,
            )
            reply = done.pop().result().decode("utf-8")
            _LOGGER.info(f'Modem replied with {reply}')

            if reply == "ERROR":
                self.terminate()
                raise Exception("Error making a voice call")
        except TimeoutError:
            _LOGGER.info(f"Assuming voice call is being made even reply to {self.at_command} wasn't received")

        await asyncio.sleep(self.call_duration + 10)

        _LOGGER.info("Hanging up...")
        GsmCallNotificationService.modem.write(b"AT+CHUP\r\n")
        self.terminate()
