# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import copy
import htmlentitydefs

import lxml.etree
import lxml.objectify
import gocept.lxml.objectify
import rwproperty

import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces.browser
import zope.security.management

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.wysiwyg.interfaces


class HTML(object):

    zope.component.adapts(zeit.wysiwyg.interfaces.IHTMLConvertable)
    zope.interface.implements(zeit.wysiwyg.interfaces.IHTMLContent)

    def __init__(self, context):
        self.context = context
        self.request = (
            zope.security.management.getInteraction().participations[0])

    @rwproperty.getproperty
    def html(self):
        """return html snippet of article."""
        # XXX spaghetti warning
        html = []
        for node in self._html_getnodes():
            # Copy all nodes. This magically removes namespace declarations.
            node = copy.copy(node)
            if node.tag == 'intertitle':
                node.tag = 'h3'
            image_nodes = node.xpath('image')
            if image_nodes:
                self._replace_image_nodes_by_img(image_nodes)
            html.append(lxml.etree.tostring(
                node, pretty_print=True, encoding=unicode))
        return '\n'.join(html)


    @rwproperty.setproperty
    def html(self, value):
        """set article html."""
        value = '<div>' + self._replace_entities(value) + '</div>'
        html = gocept.lxml.objectify.fromstring(value)
        for node in self._html_getnodes():
            parent = node.getparent()
            parent.remove(node)
        body = self.context.xml['body']
        for node in html.iterchildren():
            if not node.countchildren() and not node.text:
                continue
            if node.text and not node.text.strip():
                continue

            if node.tag == 'h3':
                node.tag = 'intertitle'
            img_nodes = node.xpath('img')
            if img_nodes:
                self._replace_img_nodes_by_image(img_nodes)
            body.append(node)

    def _html_getnodes(self):
        for node in self.context.xml['body'].iterchildren():
            if node.tag in ('p', 'intertitle'):
                yield node

    def _replace_image_nodes_by_img(self, image_nodes):
        """Replace XML <image/> by HTML <img/>."""
        for image_node in image_nodes:
            unique_id = image_node.get('src')
            if unique_id.startswith('/cms/work/'):
                unique_id = unique_id.replace(
                    '/cms/work/', zeit.cms.interfaces.ID_NAMESPACE)
            url = unique_id
            if unique_id.startswith(zeit.cms.interfaces.ID_NAMESPACE):
                try:
                    image = self.repository.getContent(unique_id)
                except KeyError:
                    pass
                else:
                    url = self.url(image)

            image_node.getparent().replace(
                image_node, lxml.objectify.E.img(src=url))

    def _replace_img_nodes_by_image(self, image_nodes):
        """Replace HTML <img/> by XML <image/>."""
        repository_url = self.url(self.repository)
        for image_node in image_nodes:
            url = image_node.get('src')
            parent = image_node.getparent()
            new_node = None
            if url.startswith(repository_url):
                unique_id = url.replace(
                    repository_url, zeit.cms.interfaces.ID_NAMESPACE)
                try:
                    image = self.repository.getContent(unique_id)
                except KeyError:
                    # Not known to the cms.
                    pass
                else:
                    new_node = zope.component.queryAdapter(
                        image, zeit.cms.content.interfaces.IXMLReference,
                        name='image')
            if new_node is None:
                new_node = lxml.objectify.E.image(src=url)
            parent.replace(image_node, new_node)

    @staticmethod
    def _replace_entities(value):
        # XXX is this efficient enough?
        for entity_name, codepoint in htmlentitydefs.name2codepoint.items():
            if entity_name in ('gt', 'lt', 'quot', 'amp', 'apos'):
                # don't replace XML built-in entities
                continue
            value = value.replace('&'+entity_name+';', unichr(codepoint))
        return value

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def url(self, obj):
        return zope.component.getMultiAdapter(
            (obj, self.request), name='absolute_url')()
