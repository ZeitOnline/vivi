import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.DocFileSuite('locking.txt', package='zeit.cms.locking')
