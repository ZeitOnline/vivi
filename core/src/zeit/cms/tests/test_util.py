from zeit.cms.util import MemoryFile
import pickle
import unittest


class MemoryFileTest(unittest.TestCase):
    def test_is_pickleable(self):
        f = MemoryFile(b'asdf')
        dumped = pickle.dumps(f)
        f = pickle.loads(dumped)
        assert f.read() == b'asdf'
