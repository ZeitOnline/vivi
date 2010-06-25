# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.cms.testing


product_config = """
<product-config zeit.preview>
    content-url file://PACKAGE/tests/fixtures
    xslt-url file://PACKAGE/tests/fixtures/stylesheets
</product-config>
""".replace('PACKAGE', pkg_resources.resource_filename('zeit.preview', ''))


layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml', product_config=product_config)
