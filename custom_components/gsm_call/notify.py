"""GSM dialer for notify component."""

from __future__ import annotations

import logging
import urllib
import serial
from time import sleep
import re

import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_DEVICE_PATH = "device_path"
CONF_AT_COMMAND = "at_command"

# TODO: Implement proper validation of the device path
# TODO: Limit CONF_AT_COMMAND only to ATD and ATDT
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE_PATH): cv.string,
        vol.Required(CONF_AT_COMMAND, default="ATD"): cv.string,
    }
)


def get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> GsmCallNotificationService:
    return GsmCallNotificationService(
        config[CONF_DEVICE_PATH],
        config[CONF_AT_COMMAND],
    )


class GsmCallNotificationService(BaseNotificationService):
    def __init__(self, device_path, at_command):
        """Initialize the service."""
        self.device_path = device_path
        self.at_command = at_command

    def send_message(self, message="", **kwargs):
        """Call to specified target users."""
        if not (targets := kwargs.get(ATTR_TARGET)):
            _LOGGER.info("At least 1 target is required")
            return

        # TODO: Validate phone numbers and check for the leading "+"
        for target in targets:
            try:
                self._dial_target(target)
            except Exception as ex:
                _LOGGER.error(ex)

    def _dial_target(self, target):
        _LOGGER.debug(f"Dialing {target}...")

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

        phone_number = re.sub("\D", "", target)

        modem.write(f'{self.at_command}+{phone_number};\r\n'.encode())

        _LOGGER.debug("ATD sent")

        sleep(35)

        _LOGGER.debug("Hanging up...")
        modem.write(b'AT+CHUP\r\n')

        modem.close()
