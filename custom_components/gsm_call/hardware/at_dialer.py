# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from homeassistant.exceptions import HomeAssistantError

from ..const import _LOGGER, CallState
from ..modem import READ_LIMIT, Modem


class ATDialer:
    at_command = "ATD"

    def __init__(self, call_duration_sec: int):
        self.call_duration = call_duration_sec + 5  # ~5 sec for a call to initialize

    async def dial(self, modem: Modem, phone_number: str) -> CallState:
        _LOGGER.debug(f"Dialing +{phone_number}...")
        modem.writer.write(f"{self.at_command}+{phone_number};\r\n".encode())

        await asyncio.sleep(1)
        _LOGGER.debug("Reading from modem...")
        buf = await modem.reader.read(READ_LIMIT)
        reply = buf.decode().strip()
        _LOGGER.debug(f"Modem replied with {reply}")

        if "ERROR" in reply or "NO CARRIER" in reply:
            raise HomeAssistantError("Modem replied with an error")

        if "BUSY" in reply:
            raise HomeAssistantError("Busy")

        _LOGGER.info(f"Ringing for {self.call_duration} seconds...")
        try:
            call_state = await asyncio.wait_for(
                self._wait_call_completion(modem),
                timeout=self.call_duration,
            )
        except asyncio.TimeoutError:
            call_state = CallState.TIMEDOUT

        _LOGGER.info(f"Call state: {call_state}")

        _LOGGER.debug("Hanging up...")
        modem.writer.write(b"AT+CHUP\r\n")

        return call_state

    async def _wait_call_completion(self, modem: Modem):
        while True:
            modem.writer.write(b"AT+CLCC\r\n")

            # Connection initializes: +CLCC: 1,0,2…
            # Phone is ringing:       +CLCC: 1,0,3…
            # Answered:               +CLCC: 1,0,0…
            # Declined:               Nothing, OK only
            await asyncio.sleep(1)
            buf = await modem.reader.read(READ_LIMIT)
            reply = buf.decode().strip()
            _LOGGER.debug(f"Modem replied with {reply}")

            if "+CLCC: 1,0,0" in reply:
                return CallState.ANSWERED

            if "+CLCC: 1,0" not in reply:
                return CallState.DECLINED
