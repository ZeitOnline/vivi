# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.content.portraitbox.portraitbox


class PortraitboxLongtext(
        zeit.content.portraitbox.portraitbox.PortraitboxHTMLContent):

    path = lxml.objectify.ObjectPath('.block.longtext')

    @property
    def longtext(self):
        # delegate to zeit.wysiwyg.html.HTMLContentBase
        return self.html

    @longtext.setter
    def longtext(self, value):
        # delegate to zeit.wysiwyg.html.HTMLContentBase
        self.html = value
