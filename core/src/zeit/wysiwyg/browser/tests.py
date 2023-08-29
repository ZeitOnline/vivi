import zeit.cms.testing
import zeit.wysiwyg.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'filebrowser.txt',
        'image.txt',
        layer=zeit.wysiwyg.testing.WSGI_LAYER)
