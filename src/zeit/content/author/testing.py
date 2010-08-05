# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zope.testing.doctest

product_config = """
<product-config zeit.content.author>
    author-folder /foo/bar/authors
</product-config>
"""

ZCMLLayer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', ZCMLLayer)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)
