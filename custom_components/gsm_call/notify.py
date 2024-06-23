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

        if GsmCallNotificationService.modem:
            _LOGGER.info("Already making a voice call")
            return

        try:
            self.connect()

            for target in targets:
                phone_number_re = re.compile(r"^\+?[1-9]\d{1,14}$")
                if not phone_number_re.match(target):
                    raise Exception("Invalid phone number")
                phone_number = re.sub(r"\D", "", target)

                await self._async_dial_target(phone_number)
        except Exception as ex:
            _LOGGER.exception(ex)
        finally:
            self.terminate()

    def connect(self):
        _LOGGER.debug(f"Connecting to {self.device_path}...")
        GsmCallNotificationService.modem = serial.Serial(
            self.device_path,
            baudrate=75600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=3,
            dsrdtr=True,
            rtscts=True,
        )

    def terminate(self):
        if GsmCallNotificationService.modem is None:
            return

        _LOGGER.debug(f"Closing connection to the modem...")
        GsmCallNotificationService.modem.close()
        GsmCallNotificationService.modem = None

    async def _async_dial_target(self, phone_number):
        _LOGGER.debug(f"Dialing +{phone_number}...")
        GsmCallNotificationService.modem.write(f"{self.at_command}+{phone_number};\r\n".encode())

        await asyncio.sleep(1)
        reply = GsmCallNotificationService.modem.read(GsmCallNotificationService.modem.in_waiting).decode()
        _LOGGER.debug(f"Modem replied with ${reply}")

        if "ERROR" in reply:
            raise Exception("Modem replied with an unknown error")

        _LOGGER.info(f"Ringing for {self.call_duration + 5} seconds...")
        await asyncio.sleep(self.call_duration + 5)

        _LOGGER.debug("Hanging up...")
        GsmCallNotificationService.modem.write(b"AT+CHUP\r\n")
