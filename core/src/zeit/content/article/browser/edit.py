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
        __traceback_info__ = (self.paragraphs, self.text)
        if self.paragraphs:
            original_keys = self.context.keys()
            insert_at = original_keys.index(self.paragraphs[0])
        else:
            insert_at = None
        for key in self.paragraphs:
            del self.context[key]
        order = list(self.context.keys())
        for text in self.text:
            if not text.strip():
                continue
            factory = zope.component.getAdapter(
                self.context, zeit.edit.interfaces.IElementFactory, name='p')
            p = factory()
            p.text = text
            if insert_at is not None:
                order.insert(insert_at, p.__name__)
                # Next insert is after the paragraph we just inserted.
                insert_at += 1
        if insert_at is not None:
            self.context.updateOrder(order)
        self.signal(
            None, 'reload',
            'editable-body', self.url(self.context, '@@contents'))
