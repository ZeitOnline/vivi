import zeit.content.cp
import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'README.txt', 'cmscontentiterable.txt', 'rule.txt', package=zeit.content.cp
    )
