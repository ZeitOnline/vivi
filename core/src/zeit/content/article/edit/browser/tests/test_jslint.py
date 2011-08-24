# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class JSLintTest(zeit.cms.testing.JSLintTestCase):

    include = ('zeit.content.article.edit.browser:resources',)
    # XXX that file has problems with spurious "unused variable" errors
    exclude = ('html.js')
