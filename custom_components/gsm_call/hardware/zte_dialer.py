# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from asyncio import StreamReader, StreamWriter, sleep
from typing import Tuple

from ..const import _LOGGER
from .at_dialer import ATDialer


class ZTEDialer(ATDialer):
    async def dial(self, modem: Tuple[StreamReader, StreamWriter], phone_number: str):
        _, writer = modem

        _LOGGER.debug("Sending ZTE's magic AT%icscall=1,0 command...")
        writer.write(b"AT%icscall=1,0\r\n")

        await sleep(1)
        return await super().dial(modem, phone_number)
