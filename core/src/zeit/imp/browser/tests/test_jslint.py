import zeit.cms.testing


class JSLintTest(zeit.cms.testing.JSLintTestCase):

    include = ('zeit.imp.browser:resources',)
    exclude = ('ui4w.js',)
    predefined = zeit.cms.testing.JSLintTestCase.predefined + (
        'UI',
    )
