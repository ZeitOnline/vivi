# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import zeit.cms.interfaces
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.wysiwyg.html
import zope.component
import zope.interface


WYSIWYGLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class WYSIWYGTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = WYSIWYGLayer


class HTMLContent(zeit.wysiwyg.html.HTMLContentBase):

    zope.component.adapts(
        zeit.cms.testcontenttype.interfaces.ITestContentType)

    def get_tree(self):
        return self.context.xml['body']
