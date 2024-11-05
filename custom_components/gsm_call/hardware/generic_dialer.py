# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from custom_components.gsm_call.const import _LOGGER


class GenericDialer:
    def __init__(self, modem, at_command, call_duration):
        self.serial = modem
        self.at_command = at_command
        self.call_duration = call_duration

    async def dial(self, phone_number):
        _LOGGER.debug(f"Dialing +{phone_number}...")
        self.serial.write(f"{self.at_command}+{phone_number};\r\n".encode())

        await asyncio.sleep(1)
        reply = self.serial.read(self.serial.in_waiting).decode()
        _LOGGER.debug(f"Modem replied with ${reply}")

        if "ERROR" in reply:
            raise Exception("Modem replied with an unknown error")

        _LOGGER.info(f"Ringing for {self.call_duration + 5} seconds...")
        await asyncio.sleep(self.call_duration + 5)

        _LOGGER.debug("Hanging up...")
        self.serial.write(b"AT+CHUP\r\n")
