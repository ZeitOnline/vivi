# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.lxml.interfaces
import grokcore.component
import lxml.objectify
import uuid
import z3c.traverser.interfaces
import zeit.content.article.edit.interfaces
import zeit.content.article.interfaces
import zeit.edit.container
import zope.publisher.interfaces


editable_body_name = 'editable-body'


class EditableBody(zeit.edit.container.Base,
                   grokcore.component.MultiAdapter):

    grokcore.component.implements(
        zeit.content.article.edit.interfaces.IEditableBody)
    grokcore.component.provides(
        zeit.content.article.edit.interfaces.IEditableBody)
    grokcore.component.adapts(zeit.content.article.interfaces.IArticle,
                              gocept.lxml.interfaces.IObjectified)

    __name__ = editable_body_name

    _find_item = lxml.etree.XPath(
        './/*[@cms:__name__ = $name]',
        namespaces=dict(
            cms='http://namespaces.zeit.de/CMS/cp'))

    def _set_default_key(self, xml_node):
        key = xml_node.get('{http://namespaces.zeit.de/CMS/cp}__name__')
        if not key:
            key = str(uuid.uuid4())
            xml_node.set('{http://namespaces.zeit.de/CMS/cp}__name__',
                         key)
            self._p_changed = True
        return key

    def _get_keys(self, xml_node):
        # XXX this is much too simple and needs work. and tests.
        result = []
        for didx, division in enumerate(
            xml_node.xpath('division[@type="page"]'), start=1):
            key = self._set_default_key(division)
            if didx > 1:
                # Skip the first division as it isn't editable
                result.append(key)
            for child in division.iterchildren():
                result.append(self._set_default_key(child))
        return result

    def _get_element_type(self, xml_node):
        return xml_node.tag

    def _add(self, item):
        # Add to last division instead of self.xml
        name = item.__name__
        if name:
            if name in self:
                raise zope.container.interfaces.DuplicateIDError(name)
        else:
            name = str(uuid.uuid4())
        item.__name__ = name
        self.xml.division[:][-1].append(item.xml)
        return name

    def _delete(self, key):
        __traceback_info__ = (key,)
        item = self[key]
        if zeit.content.article.edit.interfaces.IDivision.providedBy(item):
            # Move contained elements to previous devision
            prev = item.xml.getprevious()
            for child in item.xml.iterchildren():
                prev.append(child)
        item.xml.getparent().remove(item.xml)
        return item


@grokcore.component.adapter(zeit.content.article.interfaces.IArticle)
@grokcore.component.implementer(
    zeit.content.article.edit.interfaces.IEditableBody)
def get_editable_body(article):
    return zope.component.queryMultiAdapter(
        (article,
         zope.security.proxy.removeSecurityProxy(article.xml['body'])),
        zeit.content.article.edit.interfaces.IEditableBody)


class BodyTraverser(object):

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name == editable_body_name:
            body = zeit.content.article.edit.interfaces.IEditableBody(
                self.context, None)
            if body is not None:
                return body
        raise zope.publisher.interfaces.NotFound(self.context, name, request)
