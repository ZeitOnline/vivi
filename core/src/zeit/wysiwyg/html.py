# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import copy
import htmlentitydefs

import gocept.lxml.objectify
import lxml.etree
import lxml.objectify
import rwproperty

import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.publisher.interfaces.browser
import zope.security.management
import zope.security.proxy
import zope.traversing.interfaces

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.wysiwyg.interfaces


class HTMLConverter(object):
    """General XML to HTML converter.

    This html converter doesn't operate on `context` and is registered for all
    objects. If a content object requires a more specialised adapter it can be
    registered easily.

    """

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.wysiwyg.interfaces.IHTMLConverter)

    def __init__(self, context):
        self.context = context
        self.request = (
            zope.security.management.getInteraction().participations[0])

    def to_html(self, tree):
        """return html snippet of article."""
        tree = zope.security.proxy.removeSecurityProxy(tree)
        # XXX spaghetti warning
        html = []
        for node in self._html_getnodes(tree):
            # Copy all nodes. This magically removes namespace declarations.
            node = copy.copy(node)

            image_nodes = node.xpath('image')
            if image_nodes:
                self._replace_image_nodes_by_img(image_nodes)

            anchors = node.xpath('a')
            if anchors:
                self._replace_ids_by_urls(anchors)

            if node.tag == 'intertitle':
                node.tag = 'h3'
            elif node.tag == 'article_extra':
                new_node = lxml.objectify.XML('<p><input/></p>')
                new_node['input'].attrib.update(dict(
                        type='text',
                        name='',
                        value='%s:%s' % (node.get('id'), node.get('videoID')),
                        size='60'))
                node = new_node

            html.append(lxml.etree.tostring(
                node, pretty_print=True, encoding=unicode))
        return '\n'.join(html)


    def from_html(self, tree, value):
        """set article html."""
        tree = zope.security.proxy.removeSecurityProxy(tree)
        value = '<div>' + self._replace_entities(value) + '</div>'
        html = gocept.lxml.objectify.fromstring(value)
        for node in self._html_getnodes(tree):
            parent = node.getparent()
            parent.remove(node)
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
            anchors = node.xpath('a')
            if anchors:
                self._replace_urls_by_ids(anchors)

            if node.tag == 'p' and node.find('input') is not None:
                node = self._article_extra(node)

            tree.append(node)
        zope.security.proxy.removeSecurityProxy(self.context)._p_changed = 1

    def _html_getnodes(self, tree):
        for node in tree.iterchildren():
            if node.tag in ('p', 'intertitle', 'article_extra'):
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

            new_node = lxml.objectify.E.img(src=url)
            image_node.getparent().replace(image_node, new_node)
            new_node.tail = image_node.tail

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
            new_node.tail = image_node.tail

    def _article_extra(self, node):
        input_node = node['input']
        value = input_node.get('value')
        if ':' in value:
            id, video_id = value.split(':', 1)
        else:
            id=None
            video_id = value

        node = lxml.objectify.E.article_extra(videoID=video_id)
        if id is not None:
            node.set('id', id)
        return node

    def _replace_ids_by_urls(self, anchors):
        for anchor in anchors:
            id = anchor.get('href')
            if not id:
                continue
            anchor.set('href', self._id_to_url(id))

    def _replace_urls_by_ids(self, anchors):
        for anchor in anchors:
            url = anchor.get('href')
            if not url:
                continue
            anchor.set('href', self._url_to_id(url))

    @staticmethod
    def _replace_entities(value):
        # XXX is this efficient enough?
        for entity_name, codepoint in htmlentitydefs.name2codepoint.items():
            if entity_name in ('gt', 'lt', 'quot', 'amp', 'apos'):
                # don't replace XML built-in entities
                continue
            value = value.replace('&'+entity_name+';', unichr(codepoint))
        return value

    def _url_to_id(self, url):
        """Produce unique id from url if possible."""
        repository_url = self.url(self.repository)
        if not url.startswith(repository_url):
            return url
        path = url[len(repository_url)+1:]
        obj = zope.traversing.interfaces.ITraverser(self.repository).traverse(
            path, None)
        if not zeit.cms.interfaces.ICMSContent.providedBy(obj):
            return url
        return obj.uniqueId

    def _id_to_url(self, id):
        try:
            obj = self.repository.getContent(id)
        except (KeyError, ValueError):
            return id
        return self.url(obj)

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def url(self, obj):
        return zope.component.getMultiAdapter(
            (obj, self.request), name='absolute_url')()



class HTMLContentBase(object):
    """Base class for html content."""

    zope.interface.implements(zeit.wysiwyg.interfaces.IHTMLContent)

    def __init__(self, context):
        self.context = context

    @rwproperty.getproperty
    def html(self):
        return self.convert.to_html(self.get_tree())

    @rwproperty.setproperty
    def html(self, value):
        return self.convert.from_html(self.get_tree(), value)

    @property
    def convert(self):
        return zeit.wysiwyg.interfaces.IHTMLConverter(self.context)

    def get_tree(self):
        raise NotImplementedError("Implemented in subclass.")
