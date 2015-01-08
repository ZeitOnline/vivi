import zeit.cms.testing
import zeit.push


ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=(zeit.cms.testing.cms_product_config
                    + zeit.push.product_config))
