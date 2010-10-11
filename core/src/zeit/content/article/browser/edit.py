# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.article.edit.interfaces


class EditorContents(object):

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(
            self.context)
