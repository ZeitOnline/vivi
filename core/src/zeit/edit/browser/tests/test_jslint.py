# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class JSLintTest(zeit.cms.testing.JSLintTestCase):

    include = ('zeit.edit.browser:js',)
    exclude = (
        'MochiKit.js',
        'json-template.js',
        )
