import pkg_resources


# Break mutual dependency between zeit.push.testing and
# zeit.content.article.testing.
product_config = """\
<product-config zeit.push>
  twitter-accounts file://%s
  twitter-main-account testaccount
</product-config>
""" % pkg_resources.resource_filename(
    __name__, 'tests/fixtures/twitter-accounts.xml')
