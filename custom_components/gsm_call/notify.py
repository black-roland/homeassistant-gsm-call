# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import re

import homeassistant.helpers.config_validation as cv
import serial_asyncio_fast as serial_asyncio
import voluptuous as vol
from homeassistant.components.notify import ATTR_TARGET
from homeassistant.components.notify import PLATFORM_SCHEMA as NOTIFY_PLATFORM_SCHEMA
from homeassistant.components.notify import BaseNotificationService
from homeassistant.const import CONF_DEVICE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    _LOGGER,
    ATTR_PHONE_NUMBER,
    ATTR_REASON,
    CONF_AT_COMMAND,
    CONF_CALL_DURATION_SEC,
    CONF_HARDWARE,
    EVENT_GSM_CALL_ENDED,
)
from .hardware.at_dialer import ATDialer
from .hardware.at_tone_dialer import ATToneDialer
from .hardware.gtm382_dialer import GTM382Dialer
from .hardware.zte_dialer import ZTEDialer
from .modem import READ_LIMIT, Modem

SUPPORTED_HARDWARE = {
    "atd": ATDialer,
    "atdt": ATToneDialer,
    "zte": ZTEDialer,
    "gtm382": GTM382Dialer,
}

PLATFORM_SCHEMA = NOTIFY_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICE): cv.isdevice,
        vol.Optional(CONF_HARDWARE, default="atd"): vol.In(SUPPORTED_HARDWARE.keys()),
        vol.Optional(CONF_CALL_DURATION_SEC, default=30): cv.positive_int,
        # CONF_AT_COMMAND is replaced by CONF_HARDWARE
        vol.Optional(CONF_AT_COMMAND, default="ATD"): cv.matches_regex("^(ATD|ATDT)$"),
    }
)


def get_service(
    _hass: HomeAssistant,
    config: ConfigType,
    _discovery_info: DiscoveryInfoType | None = None,
) -> GsmCallNotificationService:
    dialer_name = config[CONF_HARDWARE]

    if config[CONF_HARDWARE] == "atd" and config[CONF_AT_COMMAND] == "ATDT":
        dialer_name = "atdt"

    dialer = SUPPORTED_HARDWARE[dialer_name](config[CONF_CALL_DURATION_SEC])

    return GsmCallNotificationService(
        config[CONF_DEVICE],
        dialer,
    )


class GsmCallNotificationService(BaseNotificationService):
    modem: Modem | None = None

    def __init__(self, device_path, dialer):
        self.device_path = device_path
        self.dialer = dialer

    async def async_send_message(self, _message="", **kwargs):
        if not (targets := kwargs.get(ATTR_TARGET)):
            _LOGGER.info("At least 1 target is required")
            return

        if GsmCallNotificationService.modem:
            _LOGGER.info("Already making a voice call")
            return

        try:
            await self.connect()

            for target in targets:
                phone_number_re = re.compile(r"^\+?[1-9]\d{1,14}$")
                if not phone_number_re.match(target):
                    raise ValueError("Invalid phone number")

                phone_number = re.sub(r"\D", "", target)

                call_state = await self.dialer.dial(self.modem, phone_number)
                self.hass.bus.async_fire(
                    EVENT_GSM_CALL_ENDED,
                    {ATTR_PHONE_NUMBER: phone_number, ATTR_REASON: call_state},
                )
        finally:
            await self.terminate()

    async def connect(self):
        _LOGGER.debug(f"Connecting to {self.device_path}...")
        GsmCallNotificationService.modem = Modem(
            *await serial_asyncio.open_serial_connection(
                url=self.device_path,
                baudrate=75600,
                bytesize=serial_asyncio.serial.EIGHTBITS,
                parity=serial_asyncio.serial.PARITY_NONE,
                stopbits=serial_asyncio.serial.STOPBITS_ONE,
                dsrdtr=True,
                rtscts=True,
                limit=READ_LIMIT,
            )
        )

    async def terminate(self):
        if GsmCallNotificationService.modem is None:
            return

        _LOGGER.debug("Closing connection to the modem...")
        GsmCallNotificationService.modem.writer.close()
        await GsmCallNotificationService.modem.writer.wait_closed()
        GsmCallNotificationService.modem = None
