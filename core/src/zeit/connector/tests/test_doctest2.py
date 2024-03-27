import zeit.cms.testing
import zeit.connector.connector
import zeit.connector.testing


def test_suite():
    # Need to put this into a separate file, otherwise gocept.pytestlayers
    # does not tear down other layers before running this.
    return zeit.connector.testing.FunctionalDocFileSuite(
        'locking.txt',
        'resource.txt',
        'search-ft.txt',
        'uuid.txt',
        'longrunning.txt',
        # 'stressing.txt',
        layer=zeit.connector.testing.DAV_CONNECTOR_LAYER,
    )
