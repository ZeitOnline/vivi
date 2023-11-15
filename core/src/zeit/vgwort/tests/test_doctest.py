import zeit.cms.testing
import zeit.vgwort.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt', layer=zeit.vgwort.testing.XMLRPC_LAYER, package='zeit.vgwort'
    )
