import zeit.cms.testing


LAYER = zeit.cms.testing.ZCMLLayer('ftesting.zcml')
WSGI_LAYER = zeit.cms.testing.WSGILayer(name='WSGILayer', bases=(LAYER,))


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=WSGI_LAYER)
