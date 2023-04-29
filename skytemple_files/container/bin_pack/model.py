#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations

from typing import List

from range_typed_integers import u32

from skytemple_files.common.util import read_u32

PADDING = bytes([0xFF] * 16)


class BinPackTocEntry:
    pointer: u32
    length: u32

    def __init__(self, data: memoryview):
        self.pointer = read_u32(data, 0)
        self.length = read_u32(data, 4)


class BinPackHeader:
    """Header for a BinPack"""

    number_files: u32

    def __init__(self, data: memoryview):
        self.number_files = read_u32(data, 4)
        self.toc: List[BinPackTocEntry] = []
        for i in range(0, self.number_files):
            self.toc.append(BinPackTocEntry(data[8 + i * 8 : 8 + (i + 1) * 8]))


class BinPack:
    def __init__(self, data: bytes):
        if not isinstance(data, memoryview):
            data = memoryview(data)
        # The header is read-only, only used during deserialization and
        # fully regenerated by the Writer. It is NOT updated during
        # the lifetime of the model.
        self._header = BinPackHeader(data)
        self._files: List[bytes] = []
        for toc_entry in self._header.toc:
            self._files.append(self._read_file(data, toc_entry))

    def _read_file(self, data: memoryview, toc_entry: BinPackTocEntry):
        s = toc_entry.pointer
        return data[s : s + toc_entry.length].tobytes()

    def get_files_bytes(self):
        """Returns the binary representation of the files (or a copy), for writing."""
        return self._files

    def __len__(self):
        return len(self._files)

    def __getitem__(self, key):
        return self._files[key]

    def __setitem__(self, key, value):
        self._files[key] = value

    def __delitem__(self, key):
        del self._files[key]

    def __iter__(self):
        return iter(self._files)

    def append(self, item):
        return self._files.append(item)
