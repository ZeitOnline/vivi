# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import copy
import datetime
import htmlentitydefs
import lxml.etree
import lxml.objectify
import rwproperty
import time
import zc.iso8601.parse
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.interface.common.idatetime
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

    xml_html_tags = {
        'intertitle': 'h3',
        'ul': 'ul',
        'ol': 'ol',
    }
    html_xml_tags = dict((value, key) for key, value in xml_html_tags.items())
    assert len(html_xml_tags) == len(xml_html_tags)

    editable_xml_nodes = frozenset(['p', 'intertitle', 'article_extra',
                                    'ul', 'ol', 'video'])

    def __init__(self, context):
        self.context = context
        self.request = (
            zope.security.management.getInteraction().participations[0])

    def to_html(self, tree):
        """return html snippet of article."""
        tree = zope.security.proxy.removeSecurityProxy(tree)
        html = []
        for node in self._html_getnodes(tree):
            # Copy all nodes. This magically removes namespace declarations.
            node = copy.copy(node)
            # XXX we should use utilities for getting the converters for a
            # node, should we not?
            for filter in (self._replace_image_nodes_by_img,
                           self._replace_ids_by_urls,
                           self._fix_xml_tag,
                           self._xml_article_extra,
                           self._xml_video,
                          ):
                node = filter(node)
                if node is None:
                    break

            if node is not None:
                html.append(lxml.etree.tostring(
                    node, pretty_print=True, encoding=unicode))
        return '\n'.join(html)


    def from_html(self, tree, value):
        """set article html."""
        tree = zope.security.proxy.removeSecurityProxy(tree)
        for node in self._html_getnodes(tree):
            parent = node.getparent()
            parent.remove(node)

        if not value:
            # We're done. Just don't do anything.
            return

        value = '<div>' + self._replace_entities(value) + '</div>'
        __traceback_info__ = (value,)
        html = lxml.objectify.fromstring(value)
        for node in html.iterchildren():
            for filter in (self._filter_empty,
                           self._fix_html_tag,
                           self._replace_img_nodes_by_image,
                           self._replace_urls_by_ids,
                           self._html_video,
                           self._html_article_extra,
                          ):
                node = filter(node)
                if node is None:
                    # Indicates that the node should be dropped.
                    break

            if node is not None:
                tree.append(node)

        zope.security.proxy.removeSecurityProxy(self.context)._p_changed = 1

    def _html_getnodes(self, tree):
        for node in tree.iterchildren():
            if node.tag in self.editable_xml_nodes:
                yield node

    def _filter_empty(self, node):
        if not node.countchildren() and not node.text:
            return
        if node.text and not node.text.strip():
            return
        return node

    def _fix_xml_tag(self, node):
        new_tag = self.xml_html_tags.get(node.tag)
        if new_tag is not None:
            node.tag = new_tag
        return node

    def _fix_html_tag(self, node):
        node.tag = self.html_xml_tags.get(node.tag, 'p')
        return node

    def _replace_image_nodes_by_img(self, node):
        """Replace XML <image/> by HTML <img/>."""
        image_nodes = node.xpath('descendant::image')
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
        return node

    def _replace_img_nodes_by_image(self, node):
        """Replace HTML <img/> by XML <image/>."""
        repository_url = self.url(self.repository)
        image_nodes = node.xpath('descendant::img')
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
        return node

    def _xml_article_extra(self, node):
        if node.tag != 'article_extra':
            return node

        # Check for videoID and replace by video tag. This is handled then by
        # the video handler
        if node.get('videoID'):
            return lxml.objectify.E.video(
                videoID=node.get('videoID'))

        extra_data = dict(node.attrib)
        value = extra_data.pop('id', '')
        if extra_data:
            extra_data = ' '.join('%s=%s' % (key, value)
                                  for key, value in extra_data.items())
            if value:
                value += ': %s' % extra_data
            else:
                value = extra_data
        new_node = lxml.objectify.XML('<p><input/></p>')
        new_node['input'].attrib.update(dict(
                type='text',
                name='',
                value=value,
                size='60'))
        return new_node

    def _html_article_extra(self, node):
        if node.tag != 'p' or node.find('input') is None:
            return node
        input_node = node['input']
        value = input_node.get('value')
        if ':' in value:
            id, extra_data = value.split(':', 1)
        elif '=' in value:
            id = None
            extra_data = value
        else:
            id = value
            extra_data = None

        data = {}

        if extra_data is not None:
            elements = extra_data.strip().split()
            data = {}
            for element in elements:
                if '=' in element:
                    key, value = element.split('=')
                else:
                    key = value = element
                data[key] = value

        if id is not None:
            data['id'] = id

        node = lxml.objectify.E.article_extra()
        invalid_counter = 0
        for key, value in data.items():
            try:
                node.set(key, value)
            except ValueError:
                # Key is not a valid attribute name.
                invalid_counter += 1
                node.set('invalid%s' % invalid_counter, '%s=%s' % (key, value))
        return node

    def _replace_ids_by_urls(self, node):
        anchors = node.xpath('a')
        for anchor in anchors:
            id = anchor.get('href')
            if not id:
                continue
            anchor.set('href', self._id_to_url(id))
        return node

    def _replace_urls_by_ids(self, node):
        anchors = node.xpath('a')
        for anchor in anchors:
            url = anchor.get('href')
            if not url:
                continue
            anchor.set('href', self._url_to_id(url))
        return node

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

    def _xml_video(self, node):
        if node.tag != 'video':
            return node
        video_id = node.get('videoID')
        expires = node.get('expires')
        format = node.get('format') or ''
        if expires:
            try:
                expires = zc.iso8601.parse.datetimetz(expires)
            except ValueError:
                expires = ''
            else:
                tz = zope.interface.common.idatetime.ITZInfo(self.request)
                expires = expires.astimezone(tz).strftime('%Y-%m-%d %H:%M')
        else:
            expires = ''

        node = lxml.objectify.E.div(
            lxml.objectify.E.div(video_id, **{'class': 'videoId'}),
            lxml.objectify.E.div(expires, **{'class': 'expires'}),
            lxml.objectify.E.div(format, **{'class': 'format'}),
            **{'class': 'video'})
        lxml.objectify.deannotate(node)
        return node

    def _html_video(self, node):
        if node.get('class') != 'video':
            return node

        video_id = expires = format = ''

        nodes = node.xpath('div[@class="videoId"]')
        if nodes:
            video_id = unicode(nodes[0])
        nodes = node.xpath('div[@class="expires"]')
        if nodes:
            expires = unicode(nodes[0])
            try:
                expires = datetime.datetime(
                    *(time.strptime(expires, '%Y-%m-%d %H:%M')[0:6]))
            except ValueError:
                expires = ''
            else:
                tz = zope.interface.common.idatetime.ITZInfo(self.request)
                expires = expires.replace(tzinfo=tz)
                expires = expires.isoformat()
        nodes = node.xpath('div[@class="format"]')
        if nodes:
            format = unicode(nodes[0])
        video = lxml.objectify.E.video(videoID=video_id, expires=expires,
                                       format=format)
        return video

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
