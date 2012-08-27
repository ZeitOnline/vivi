# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class JSLintTest(zeit.cms.testing.JSLintTestCase):

    include = ('zeit.imp.browser:resources',)
    exclude = ('ui.uncompressed.js',)
    predefined = zeit.cms.testing.JSLintTestCase.predefined + (
        'UI',
        )
