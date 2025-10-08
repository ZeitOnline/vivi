import doctest
import unittest

import transaction
import zope.component

from zeit.cms.repository.folder import Folder
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.repository.interfaces
import zeit.cms.testing


class FixtureLayer(zeit.cms.testing.Layer):
    def setUp(self):
        with self['rootFolder'](self['zodbDB-layer']) as root:
            with zeit.cms.testing.site(root):
                repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
                repository['online'] = Folder()
                repository['2007'] = Folder()
                repository['2007']['01'] = Folder()
                repository['online']['2007'] = Folder()
                repository['online']['2007']['01'] = Folder()

                repository['online']['2007']['01']['Somalia'] = ExampleContentType()
                repository['online']['2007']['01']['4schanzentournee-abgesang'] = (
                    ExampleContentType()
                )

                transaction.commit()


LAYER = FixtureLayer(zeit.cms.testing.ZOPE_LAYER)
WSGI_LAYER = zeit.cms.testing.WSGILayer(LAYER)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocFileSuite(
            'form.txt', package='zeit.cms.browser', optionflags=zeit.cms.testing.optionflags
        )
    )
    suite.addTest(
        zeit.cms.testing.FunctionalDocFileSuite(
            'README.txt',
            'error-views.txt',
            'listing.txt',
            'sourceedit.txt',
            'widget.txt',
            package='zeit.cms.browser',
            layer=WSGI_LAYER,
        )
    )
    return suite
