# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio

from ..const import _LOGGER, EndedReason
from ..modem import Modem
from .at_dialer import ATDialer


class GTM382Dialer(ATDialer):
    async def dial(self, modem: Modem, phone_number: str) -> EndedReason:
        _LOGGER.debug("Sending AT_ODO=0 to enable circuit-switched data transfer...")
        modem.writer.write(b"AT_ODO=0\r\n")
        await asyncio.sleep(.5)

        _LOGGER.debug("Sending AT_OPCMENABLE=1 to enable digital voice...")
        modem.writer.write(b"AT_OPCMENABLE=1\r\n")
        await asyncio.sleep(.5)

        return await super().dial(modem, phone_number)
