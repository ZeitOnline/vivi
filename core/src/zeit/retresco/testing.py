import zeit.cms.testing


product_config = """
<product-config zeit.retresco>
    base-url http://localhost:[PORT]
</product-config>
"""

ZCML_LAYER = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config
    + product_config)
