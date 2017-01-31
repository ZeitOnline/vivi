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
  facebook-campus-account fb-campus
  push-target-url http://www.zeit.de/
  mobile-image-url http://img.zeit.de/
  channel-breaking Eilmeldung
  channel-news News
  urbanairship-audience-group subscriptions
  urbanairship-ios-segment 77c49d90-f6ca-465c-b33f-110f1cdcdacd
</product-config>
""".format(fixtures=pkg_resources.resource_filename(
    __name__, 'tests/fixtures'))
