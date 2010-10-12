# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.edit.browser.view
import zope.component


class EditorContents(object):

    @property
    def body(self):
        return zeit.content.article.edit.interfaces.IEditableBody(
            self.context)


class SaveText(zeit.edit.browser.view.Action):

    text = zeit.edit.browser.view.Form('text')
    paragraphs = zeit.edit.browser.view.Form('paragraphs')

    def update(self):
        if self.paragraphs:
            original_keys = self.context.keys()
            insert_at = original_keys.index(self.paragraphs[0])
        else:
            insert_at = None
        for key in self.paragraphs:
            del self.context[key]
        order = self.context.keys()
        for i, text in enumerate(self.text):
            if not text.strip():
                continue
            factory = zope.component.getAdapter(
                self.context, zeit.edit.interfaces.IElementFactory, name='p')
            p = factory()
            p.text = text
            if insert_at:
                order.insert(insert_at + i, p.__name__)
        if insert_at:
            self.context.updateOrder(order)
