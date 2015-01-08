import unittest


class HitColumnTest(unittest.TestCase):

    def test_sort_key(self):
        import zeit.cms.browser.listing

        class TestAccessCounter(object):
            hits = 5
            total_hits = 19

        column = zeit.cms.browser.listing.HitColumn(
            getter=lambda i, f: i)
        self.assertEquals((19, 5),
                          column.getSortKey(TestAccessCounter(),
                                            formatter=None))
