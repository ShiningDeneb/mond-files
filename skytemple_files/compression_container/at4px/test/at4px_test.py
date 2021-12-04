#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
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
# mypy: ignore-errors
import os
from typing import Type

import pytest
from parameterized import parameterized

from skytemple_files.common.impl_cfg import ENV_SKYTEMPLE_USE_NATIVE, env_use_native
from skytemple_files.compression_container.at4px.handler import At4pxHandler
from skytemple_files.compression_container.protocol import CompressionContainerProtocol
from skytemple_files.compression_container.test.util import load_dataset, dataset_name_func

from skytemple_files.test.case import SkyTempleFilesTestCase, fixpath

FIX = b'Hello World. I am testing compression. 123456789. 11223344. 12121213.'


class At4pxTestCase(SkyTempleFilesTestCase[At4pxHandler, CompressionContainerProtocol]):
    @classmethod
    def handler(cls) -> Type[At4pxHandler]:
        return At4pxHandler

    def test_cross_px_native_implementation_compress(self):
        """Tests the native implementation against the Python implementation (assuming this one works)"""
        if not env_use_native():
            self.skipTest("This test is only enabled when the native implementations are tested.")
        py_cls = self.handler().load_python_model()
        rs_cls = self.handler().load_native_model()
        result_rs = rs_cls.compress(FIX).to_bytes()
        self.assertEqual(
            FIX, bytes(py_cls(result_rs).decompress()),
            "The rust implementation mus compress correctly, so the Python implementation "
            "can correctly decompress it again."
        )

    def test_cross_px_native_implementation_decompress(self):
        """Tests the native implementation against the Python implementation (assuming this one works)"""
        if not env_use_native():
            self.skipTest("This test is only enabled when the native implementations are tested.")
        py_cls = self.handler().load_python_model()
        rs_cls = self.handler().load_native_model()
        result_py = py_cls.compress(FIX).to_bytes()
        self.assertEqual(
            FIX, rs_cls(result_py).decompress(),
            "The rust implementation mus decompress correctly."
        )

    def test_simple_compression(self):
        model = self.handler().compress(FIX)
        self.assertEqual(FIX, model.decompress())

    @parameterized.expand(load_dataset(), name_func=dataset_name_func)
    def test_container(self, _, in_bytes):
        model = self.handler().compress(in_bytes)
        self.assertEqual(len(model.to_bytes()), model.cont_size(model.to_bytes()))
        self.assertTrue(model.to_bytes().startswith(b'AT4PX'))
        self.assertEqual(model.to_bytes(), self.handler().serialize(self.handler().deserialize(model.to_bytes())))
        self.assertEqual(in_bytes, model.decompress())

    def test_game_content_decompress(self):
        with open(self._fix_path_uncompressed(), 'rb') as f:
            in_decompressed = f.read()
        with open(self._fix_path_compressed(), 'rb') as f:
            in_compressed = f.read()
        decompressed = self.handler().deserialize(in_compressed).decompress()
        self.assertEqual(in_decompressed, decompressed)

    @classmethod
    @fixpath
    def _fix_path_uncompressed(cls):
        return 'fixtures', 'portrait.bin'

    @classmethod
    @fixpath
    def _fix_path_compressed(cls):
        return 'fixtures', 'portrait_compressed.bin'
