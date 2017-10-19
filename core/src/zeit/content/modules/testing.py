import pkg_resources


product_config = """\
<product-config zeit.content.modules>
  jobticker-source file://{base}/tests/fixtures/jobticker.xml
</product-config>
""".format(base=pkg_resources.resource_filename(__name__, '.'))
