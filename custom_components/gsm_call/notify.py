"""GSM dialer for notify component."""

from __future__ import annotations

import logging
import urllib
import serial
from time import sleep
import re
import asyncio

import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_AT_COMMAND = "at_command"
CONF_CALL_DURATION = "call_duration"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE): cv.isdevice,
        vol.Required(CONF_AT_COMMAND, default="ATD"): cv.matches_regex("^(ATD|ATDT)$"),
        vol.Required(CONF_CALL_DURATION, default=30): cv.positive_int,
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
        config[CONF_CALL_DURATION],
    )


class GsmCallNotificationService(BaseNotificationService):
    def __init__(self, device_path, at_command, call_duration):
        """Initialize the service."""
        self.device_path = device_path
        self.at_command = at_command
        self.call_duration = call_duration

    # TODO: Prevent parallel calls
    async def async_send_message(self, message="", **kwargs):
        """Call to specified target users."""
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
                _LOGGER.error(ex)

    async def _async_dial_target(self, phone_number):
        _LOGGER.debug("Dialing...")

        modem = serial.Serial(
            self.device_path,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=3,
            dsrdtr=True,
            rtscts=True,
        )

        modem.write(f'{self.at_command}+{phone_number};\r\n'.encode())

        _LOGGER.debug("ATD sent")

        await asyncio.sleep(self.call_duration + 10)

        _LOGGER.debug("Hanging up...")
        modem.write(b'AT+CHUP\r\n')

        modem.close()
