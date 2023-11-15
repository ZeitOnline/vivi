import zeit.cms.testing


class JSLintTest(zeit.cms.testing.JSLintTestCase):
    include = ('zeit.content.article.edit.browser:resources',)
    exclude = ('jsuri.js',)
