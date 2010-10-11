# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.interfaces


class EditorContents(object):

    @property
    def body(self):
        return zeit.content.article.interfaces.IEditableBody(self.context)
