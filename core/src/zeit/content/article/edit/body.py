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
import zeit.edit.rule
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
        if self.xml.find('division') is None:
            self._migrate()
        for didx, division in enumerate(
            xml_node.xpath('division[@type="page"]'), start=1):
            key = self._set_default_key(division)
            if didx > 1:
                # Skip the first division as it isn't editable
                result.append(key)
            for child in division.iterchildren():
                result.append(self._set_default_key(child))
        return result

    def _migrate(self):
        division = lxml.objectify.E.division(type='page')
        self.xml.append(division)
        for node in self.xml.getchildren():
            if node.tag == 'division':
                # Ignore the division we've just added to the body
                continue
            element = self._get_element_for_node(node)
            if element:
                division.append(node)

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
            # may migrate so it is guaranteed that there is a division tag:
            self.keys()
        item.__name__ = name
        self.xml.division[:][-1].append(item.xml)
        self._p_changed = True
        return name

    def _delete(self, key):
        __traceback_info__ = (key,)
        item = self[key]
        assert item is not None
        if zeit.content.article.edit.interfaces.IDivision.providedBy(item):
            # Move contained elements to previous devision
            prev = item.xml.getprevious()
            for child in item.xml.iterchildren():
                prev.append(child)
        item.xml.getparent().remove(item.xml)
        self._p_changed = True
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


# Remove all the __name__ thingies on checkin.
# NOTE: this code is *not* really used right now. A browser test makes sure the
# attributes are removed and it passes because the article's body is mangled
# through zeit.wysiwyg.html on checkin which also removes everything it doesn't
# know about. Once #8194 is implemented the name attributes will no longer be
# removed automatically. This code should be activated then.

_find_name_attributes = lxml.etree.XPath(
    './/*[@cms:__name__]',
    namespaces=dict(cms='http://namespaces.zeit.de/CMS/cp'))

def clean_names_on_checkin(context):
    for element in _find_name_attributes(context.xml):
        del element.attrib['{http://namespaces.zeit.de/CMS/cp}__name__']


class ArticleValidator(zeit.edit.rule.RecursiveValidator,
                       grokcore.component.Adapter):

    grokcore.component.context(zeit.content.article.interfaces.IArticle)

    @property
    def children(self):
        body = zeit.content.article.edit.interfaces.IEditableBody(self.context)
        return body.values()
