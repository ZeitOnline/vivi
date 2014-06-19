import pkg_resources


# Break mutual dependency between zeit.push.testing and
# zeit.content.article.testing.
product_config = """\
<product-config zeit.push>
  twitter-accounts file://{fixtures}/twitter-accounts.xml
  twitter-main-account twitter-test
  facebook-accounts file://{fixtures}/facebook-accounts.xml
  facebook-main-account fb-test
  facebook-magazin-account fb-magazin
</product-config>
""".format(fixtures=pkg_resources.resource_filename(
    __name__, 'tests/fixtures'))
