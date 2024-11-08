# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from asyncio import StreamReader, StreamWriter
from typing import Tuple

import serial_asyncio_fast as serial_asyncio

READ_LIMIT = 2**16  # 64 KiB


class Modem:
    reader: StreamReader
    writer: StreamWriter
    serial: serial_asyncio.serial.Serial

    def __init__(self, connection: Tuple[StreamReader, StreamWriter]):
        self.reader = connection[0]
        self.writer = connection[1]
        self.serial = self.writer.transport.get_extra_info("serial")
