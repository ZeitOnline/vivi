import doctest
import zeit.cms.testing


def test_suite():
    return doctest.DocFileSuite(
        'README.txt', package='zeit.cms.workingcopy', optionflags=zeit.cms.testing.optionflags
    )
