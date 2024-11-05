# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from ..const import _LOGGER


class GenericDialer:
    def __init__(self, at_command, call_duration):
        self.at_command = at_command
        self.call_duration = call_duration

    async def dial(self, modem, phone_number):
        _LOGGER.debug(f"Dialing +{phone_number}...")
        modem.write(f"{self.at_command}+{phone_number};\r\n".encode())

        await asyncio.sleep(1)
        reply = modem.read(modem.in_waiting).decode()
        _LOGGER.debug(f"Modem replied with ${reply}")

        if "ERROR" in reply:
            raise Exception("Modem replied with an unknown error")

        _LOGGER.info(f"Ringing for {self.call_duration + 5} seconds...")
        await asyncio.sleep(self.call_duration + 5)

        _LOGGER.debug("Hanging up...")
        modem.write(b"AT+CHUP\r\n")
