# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import z3c.traverser.interfaces
import zeit.edit.container
import zope.publisher.interfaces


editable_body_name = 'editable-body'


class EditableBody(zeit.edit.container.Base,
                   grokcore.component.MultiAdapter):

    grokcore.component.implements(zeit.edit.interfaces.IArea)
    grokcore.component.provides(zeit.content.article.interfaces.IEditableBody)
    grokcore.component.adapts(zeit.content.article.interfaces.IArticle,
                              gocept.lxml.interfaces.IObjectified)

    __name__ = editable_body_name

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


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(zeit.content.article.interfaces.IEditableBody)
def get_editable_body(article):
    return zope.component.queryMultiAdapter(
        (article,
         zope.security.proxy.removeSecurityProxy(article.xml['body'])),
        zeit.content.article.interfaces.IEditableBody)


class BodyTraverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name == editable_body_name:
            body = zeit.content.article.interfaces.IEditableBody(
                self.context, None)
            if body is not None:
                return body
        raise zope.publisher.interfaces.NotFound(self.context, name, request)
