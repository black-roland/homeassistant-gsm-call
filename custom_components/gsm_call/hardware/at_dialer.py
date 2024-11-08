# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from homeassistant.exceptions import HomeAssistantError

from ..const import _LOGGER
from ..modem import READ_LIMIT, Modem


class ATDialer:
    at_command = "ATD"

    def __init__(self, call_duration):
        self.call_duration = call_duration

    async def dial(self, modem: Modem, phone_number: str):
        _LOGGER.debug(f"Dialing +{phone_number}...")
        modem.writer.write(f"{self.at_command}+{phone_number};\r\n".encode())

        await asyncio.sleep(1)
        _LOGGER.debug("Reading from modem...")
        buf = await modem.reader.read(READ_LIMIT)
        reply = buf.decode().strip()
        _LOGGER.debug(f"Modem replied with ${reply}")

        if "ERROR" in reply or "NO CARRIER" in reply:
            raise HomeAssistantError("Modem replied with an unknown error")

        if "BUSY" in reply:
            raise HomeAssistantError("Busy")

        sleep_duration = self.call_duration + 5
        _LOGGER.info(f"Ringing for {sleep_duration} seconds...")
        await asyncio.sleep(sleep_duration)

        _LOGGER.debug("Hanging up...")
        modem.writer.write(b"AT+CHUP\r\n")
