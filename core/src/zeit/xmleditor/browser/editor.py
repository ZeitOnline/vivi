# vim: fileencoding=utf8 encoding=utf8
# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import re
import os.path
import sys

import json
import decorator
import lxml.etree

import transaction
import zope.exceptions.interfaces
import zope.interface
import zope.proxy

import zope.app.pagetemplate.engine

import zeit.xmleditor.browser.interfaces


def xslt_getNodePath(dummy, nodes):
    return getNodePath(nodes[0])

def getNodePath(node):
    path = []
    for ancestor in node.iterancestors():
        path.append(ancestor.index(node) + 1)
        node = ancestor
    path.reverse()
    return '/*[1]/' + '/'.join('*[%s]' % x for x in path)


@decorator.decorator
def ajax(method, *args, **kwargs):

    def success(value):
        return {'error': False,
                'value': value}

    def error(exception):
        return {'error': True,
                'value': unicode(exception)}

    try:
        value = method(*args, **kwargs)
    except Exception, e:
        transaction.abort()
        result = error(e)
    else:
        result = success(value)
    return json.dumps(result)


class Editor(object):
    """XML-Editor."""

    zope.interface.implements(zeit.xmleditor.browser.interfaces.IXMLEditor)

    CHILDREN = {}
    DEFAULT_PREFIXES = {
        'http://www.w3.org/2001/XInclude': 'xi',
    }
    title = "XML-Editor"

    index = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile(
        os.path.join(os.path.dirname(__file__), 'editor.pt'))

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()

    def contentChanged(self):
        # Gaah. I really would like persistent objectifieds.
        self.context.xml = self.xml

    @property
    def xml(self):
        return zope.proxy.removeAllProxies(self.context.xml)

    @property
    def xml_source(self):
        ns = lxml.etree.FunctionNamespace("http://www.zeit.de/exslt")
        ns['nodepath'] = xslt_getNodePath
        rendered_html = str(self.xslt(zope.proxy.removeAllProxies(self.xml)))
        __traceback_info__ = (rendered_html, )
        value = lxml.etree.XML(rendered_html)
        return lxml.etree.tounicode(value, pretty_print=True)

    @classmethod
    def load_xslt(cls):
        cls.xslt = lxml.etree.XSLT(lxml.etree.parse(cls.XSLT))


class XMLEditorActions(object):

    TAG_PATTERN = re.compile(r'({(?P<namespace>.+)})?(?P<tag>.+)')

    _actions = (
        {"image": "edit_element.png",
         "title": "Bearbeiten",
         "action": 'handleShowEditTextViewEvent',
         "filter": "view/queryNodeEditor | nothing"},
        {"image": "insert.png",
         "title": "Kind einfuegen",
         'filter': 'python: view.getPossibleChildren(node)',
         "action":'handleShowAppendChildEvent',
         "drop-action": "dropAppendChild", },
        {"image": "insert_before.png",
         "title": u"Davor einfügen",
         "filter": 'python:view.getPossibleChildren(node.getparent())',
         "action":'handleShowInsertBeforeEvent',
         "drop-action": "dropInsertBefore", },
        {"image": "insert_after.png",
         "title": u"Dahinter einfügen",
         'filter': 'python:view.getPossibleChildren(node.getparent())',
         "action":'handleShowInsertAfterEvent',
         "drop-action": "dropInsertAfter", },
        {"image": "delete.png",
         "title": u"Löschen",
         "action": 'handleRemoveNodeEvent'},
        {"image": "close.png",
         "title": u"Schließen",
         "action": "hideActions"},
    )

    @property
    def actions(self):
        filter_context = zope.app.pagetemplate.engine.Engine.getContext(
            context=self.context,
            view=self,
            nothing=None,
            request=self.request,
            modules=sys.modules,
            node=self.context_node)

        for action in self._actions:
            include = True
            if action.get('filter'):
                filter = zope.app.pagetemplate.engine.Engine.compile(
                    action['filter'])
                include = filter(filter_context)
            if include:
                yield action

    @zope.cachedescriptors.property.Lazy
    def context_node(self):
        path = self.request.form['path']
        nodes = self.context.xml.xpath(path)
        if not nodes:
            raise ValueError("Path %r did not result in any nodes" % path)
        if len(nodes) != 1:
            raise ValueError("Path %r resulted in more than one node: %r" % (
                path, nodes))
        node = nodes[0]
        return node

    def getXMLSource(self):
        return self.context.xml_source

    def getLocalName(self, tag_name):
        m = self.TAG_PATTERN.match(tag_name)
        if m is None:
            raise ValueError("Invalid tag name: %s" % tag_name)
        ns = m.group('namespace')
        tag = m.group('tag')
        if ns:
            local_ns_prefix = None
            for localname, namespace in self.context.xml.nsmap.items():
                if namespace == ns:
                    local_ns_prefix = localname
            if not local_ns_prefix:
                local_ns_prefix = self.context.DEFAULT_PREFIXES.get(ns)
            if not local_ns_prefix:
                raise ValueError("Cannot find prefix for %s" % ns)
            local_name = '%s:%s' % (local_ns_prefix, tag)
        else:
            local_name = tag
        return local_name

    def remove(self):
        node = self.context_node
        node.getparent().remove(node)
        self.context.contentChanged()
        return self.context.xml_source

    def getPossibleChildren(self, node):
        return self.context.CHILDREN.get(node.tag, ())

    def getPossibleChildrenForAction(self, action):
        return self.getPossibleChildren(self.getAddChildNode(action))

    def getAddChildNode(self, action):
        node = self.context_node
        if action in ('insert-before', 'insert-after'):
            return node.getparent()
        if action == 'append-child':
            return node
        raise ValueError("Invalid action: %s" % action)

    @ajax
    def appendChild(self, action, tag):
        insert_into = self.getAddChildNode(action)
        new_node = insert_into.makeelement(tag)
        self._insert_new_node(action, new_node)
        return {'xml': self.context.xml_source,
                'node-path': getNodePath(new_node)}

    @ajax
    def dropAppendChild(self, action, unique_id):
        insert_into = self.getAddChildNode(action)
        content = self.repository.getContent(unique_id)
        reference = zope.component.queryAdapter(
            content,
            zeit.xmleditor.interfaces.IXMLReference,
            name='body')
        if reference is None:
            raise zope.exceptions.interfaces.UserError(
                "Don't know how to add %s here." % unique_id)
        self._insert_new_node(action, reference)
        return self.context.xml_source

    @property
    def node_content(self):
        node = self.context_node
        return unicode(node)

    def editNode(self, value):
        self.context_node[:] = [value]
        self.context.contentChanged()
        return self.context.xml_source

    def queryNodeEditor(self):
        node = self.context_node
        editable = zeit.xmleditor.interfaces.IEditableStructure(node, None)
        if editable is None:
            return None
        view = zope.component.queryMultiAdapter(
            (editable, self.request),
            name='edit_structure.html')
        return view

    def viewNodeEditor(self):
        view = self.queryNodeEditor()
        if view is None:
            raise ValueError("Cannot get editing form for node: %s" %
                             self.context_node)
        data = view()
        if self.request.method == 'POST':
            # XXX this is not always true, on validaation errors the data is
            # not changed.
            self.context.contentChanged()
        return data

    def _insert_new_node(self, action, node):
        insert_into = self.getAddChildNode(action)
        if node.tag not in self.getPossibleChildren(insert_into):
            raise zope.exceptions.interfaces.UserError(
                "You cannot add <%s> here." % node.tag)
        if action == 'append-child':
            insert_into.append(node)
        elif action == 'insert-before':
            index = insert_into.index(self.context_node)
            insert_into.insert(index, node)
        elif action == 'insert-after':
            index = insert_into.index(self.context_node) + 1
            insert_into.insert(index, node)
        else:
            raise ValueError("Invalid action: %s" % action)
        self.context.contentChanged()

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
