# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass

READ_LIMIT = 2**16  # 64 KiB


@dataclass(frozen=True)
class Modem:
    reader: StreamReader
    writer: StreamWriter
