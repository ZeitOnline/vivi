import pickle
import unittest

from zeit.cms.util import MemoryFile


class MemoryFileTest(unittest.TestCase):
    def test_is_pickleable(self):
        f = MemoryFile(b'asdf')
        dumped = pickle.dumps(f)
        f = pickle.loads(dumped)
        assert f.read() == b'asdf'
