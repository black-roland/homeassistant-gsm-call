# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from asyncio import StreamReader, StreamWriter, sleep
from typing import Tuple

from ..const import _LOGGER


class ATDialer:
    at_command = "ATD"

    def __init__(self, call_duration):
        self.call_duration = call_duration

    async def dial(self, modem: Tuple[StreamReader, StreamWriter], phone_number: str):
        reader, writer = modem

        _LOGGER.debug(f"Dialing +{phone_number}...")
        writer.write(f"{self.at_command}+{phone_number};\r\n".encode())

        await sleep(1)
        _LOGGER.debug("Reading from modem...")
        buf = await reader.read(128)
        reply = buf.decode().strip()
        _LOGGER.debug(f"Modem replied with ${reply}")

        if "ERROR" in reply:
            raise Exception("Modem replied with an unknown error")

        sleep_duration = self.call_duration + 5
        _LOGGER.info(f"Ringing for {sleep_duration} seconds...")
        await sleep(sleep_duration)

        _LOGGER.debug("Hanging up...")
        writer.write(b"AT+CHUP\r\n")
