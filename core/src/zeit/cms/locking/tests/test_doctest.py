import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite('locking.txt', package='zeit.cms.locking')
