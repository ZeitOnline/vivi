# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import copy
import gocept.lxml.interfaces
import grokcore.component
import lxml.etree
import lxml.objectify
import zeit.content.article.edit.interfaces
import zeit.edit.block
import zeit.edit.interfaces
import zope.component


class Paragraph(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(
      zeit.content.article.edit.interfaces.IEditableBody,
      gocept.lxml.interfaces.IObjectified)
    grokcore.component.name('p')
    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IParagraph)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IParagraph)

    type = 'paragraph'

    @property
    def text(self):
        # The copy.copy magically removes unnecessary namespace declarations.
        p_text = self.xml.text or ''
        return p_text + ''.join(
            lxml.etree.tostring(copy.copy(c)) for c in self.xml.iterchildren())

    @text.setter
    def text(self, value):
        # XXX I guess we need to munge at least <a href> here in some way.
        try:
            p = lxml.objectify.XML('<p>%s</p>' % value)
        except lxml.etree.XMLSyntaxError:
            raise ValueError('No valid XML: %s' % (value,))
        p.attrib.update(self.xml.attrib.items())
        self.xml.getparent().replace(self.xml, p)
        self.xml = p


class ParagraphFactory(grokcore.component.Adapter):

    grokcore.component.implements(zeit.edit.interfaces.IElementFactory)
    grokcore.component.context(
        zeit.content.article.edit.interfaces.IEditableBody)
    grokcore.component.name('p')

    title = u'Paragraph'
    element_type = 'p'

    def __call__(self):
        p = lxml.objectify.E.p()
        content = zope.component.getMultiAdapter(
            (self.context, p),
            zeit.edit.interfaces.IElement,
            name=self.element_type)
        self.context.add(content)
        return content
