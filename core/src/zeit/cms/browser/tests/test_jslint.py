import zeit.cms.testing


class JSLintTest(zeit.cms.testing.JSLintTestCase):
    include = ('zeit.cms.browser:js',)
    exclude = (
        'MochiKit.js',
        'json-template.js',
    )
