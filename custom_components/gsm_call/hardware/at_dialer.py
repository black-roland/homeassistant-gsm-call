# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from homeassistant.exceptions import HomeAssistantError

from ..const import _LOGGER, EndedReason
from ..modem import READ_LIMIT, Modem


class ATDialer:
    at_command = "ATD"

    def __init__(self, call_duration_sec: int):
        self.duration_sec = call_duration_sec

    async def dial(self, modem: Modem, phone_number: str) -> EndedReason:
        _LOGGER.debug(f"Dialing +{phone_number}...")
        modem.writer.write(f"{self.at_command}+{phone_number};\r\n".encode())
        await asyncio.sleep(1)

        _LOGGER.debug("Reading from the modem...")
        try:
            async with asyncio.timeout(10):
                buf = await modem.reader.read(READ_LIMIT)
                reply = buf.decode().strip()
                _LOGGER.debug(f"Modem replied with {reply}")
        except asyncio.TimeoutError:
            raise HomeAssistantError("Timed out reading from the modem")

        if "BUSY" in reply:
            raise HomeAssistantError("Busy")

        if "ERROR" in reply or "NO CARRIER" in reply:
            raise HomeAssistantError(f"Modem replied with an error: {reply}")

        try:
            _LOGGER.debug("Waiting for an answer...")
            ended_reason = await self._wait_for_answer(modem)
        except asyncio.TimeoutError:
            ended_reason = EndedReason.NOT_ANSWERED

        _LOGGER.debug("Hanging up...")
        modem.writer.write(b"AT+CHUP\r\n")
        _LOGGER.info(f"Call ended: {ended_reason}")

        return ended_reason

    async def _wait_for_answer(self, modem: Modem):
        is_ringing = False
        async with asyncio.timeout(self.duration_sec) as timeout:
            while True:
                modem.writer.write(b"AT+CLCC\r\n")

                # Provisioning:     +CLCC: 1,0,2…
                # Phone is ringing: +CLCC: 1,0,3…
                # Answered:         +CLCC: 1,0,0…
                # Declined:         Nothing, OK only
                await asyncio.sleep(1)
                buf = await modem.reader.read(READ_LIMIT)
                reply = buf.decode().strip()
                _LOGGER.debug(f"Modem replied with {reply}")

                if not is_ringing and "+CLCC: 1,0,3" in reply:
                    is_ringing = True
                    _LOGGER.info(
                        f"Callee's phone started ringing, waiting for {self.duration_sec} seconds..."
                    )
                    new_deadline = asyncio.get_running_loop().time() + self.duration_sec
                    timeout.reschedule(new_deadline)
                    continue

                if "+CLCC: 1,0,0" in reply:
                    return EndedReason.ANSWERED

                if "+CLCC: 1,0" not in reply:
                    return EndedReason.DECLINED
