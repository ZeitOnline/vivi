# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import zeit.edit.container


class EditableBody(zeit.edit.container.Base,
                   grokcore.component.MultiAdapter):

    grokcore.component.provides(zeit.edit.interfaces.IArea)
    grokcore.component.adapts(zeit.content.article.interfaces.IArticle,
                              gocept.lxml.interfaces.IObjectified)

    def _find_item(self, xml_node, name):
        __traceback_info__ = (name,)
        xpath = name.replace('.', '/')
        return xml_node.xpath(xpath)

    def _get_keys(self, xml_node):
        # XXX this is much too simple and needs work. and tests.
        result = []
        for didx, division in enumerate(
            xml_node.xpath('division[@type="page"]'), start=1):
            division_path = '%s[%s]' % (division.tag, didx)
            if didx > 1:
                # Skip the first division as it isn't editable
                result.append(division_path)
            for cidx, child in enumerate(division.iterchildren(), start=1):
                result.append(
                    '%s.*[%s]' % (division_path, cidx))
        return result

    def _get_element_type(self, xml_node):
        return xml_node.tag


class Paragraph(zeit.edit.block.Element,
                grokcore.component.MultiAdapter):

    grokcore.component.adapts(EditableBody,
                              gocept.lxml.interfaces.IObjectified)
    grokcore.component.name('p')
    grokcore.component.provides(zeit.edit.interfaces.IElement)
