# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.cms.testing
import zope.testing.doctest


layer = zope.app.testing.functional.ZCMLLayer(
    pkg_resources.resource_filename(__name__, 'ftesting.zcml'),
    __name__, __name__, allow_teardown=True)


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', layer)
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = layer
