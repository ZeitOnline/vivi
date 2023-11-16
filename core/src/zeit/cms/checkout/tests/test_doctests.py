import zeit.cms.checkout
import zeit.cms.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite('README.txt', package=zeit.cms.checkout)
