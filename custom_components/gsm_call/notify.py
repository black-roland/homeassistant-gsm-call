# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

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

from custom_components.gsm_call.const import (
    _LOGGER,
    CONF_AT_COMMAND,
    CONF_CALL_DURATION_SEC,
    CONF_HARDWARE,
)
from custom_components.gsm_call.hardware.generic_dialer import GenericDialer
from custom_components.gsm_call.hardware.zte_dialer import ZteDialer


SUPPORTED_HARDWARE = {
    "generic": GenericDialer,
    "zte": ZteDialer,
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE): cv.isdevice,
        vol.Optional(CONF_HARDWARE, default="generic"): vol.In(
            SUPPORTED_HARDWARE.keys()
        ),
        vol.Optional(CONF_AT_COMMAND, default="ATD"): cv.matches_regex("^(ATD|ATDT)$"),
        vol.Optional(CONF_CALL_DURATION_SEC, default=25): cv.positive_int,
    }
)


def get_service(
    _hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> GsmCallNotificationService:
    dialer_name = config[CONF_HARDWARE]
    dialer = SUPPORTED_HARDWARE[dialer_name](
        config[CONF_AT_COMMAND], config[CONF_CALL_DURATION_SEC]
    )

    return GsmCallNotificationService(
        config[CONF_DEVICE],
        dialer,
    )


class GsmCallNotificationService(BaseNotificationService):
    modem: serial.Serial | None = None

    def __init__(self, device_path, dialer):
        self.device_path = device_path
        self.dialer = dialer

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

                await self.dialer.dial(self.modem, phone_number)
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

        _LOGGER.debug("Closing connection to the modem...")
        GsmCallNotificationService.modem.close()
        GsmCallNotificationService.modem = None
