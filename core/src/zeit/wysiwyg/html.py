# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import copy
import datetime
import htmlentitydefs
import lxml.etree
import lxml.objectify
import rwproperty
import time
import xml.sax.saxutils
import zc.iso8601.parse
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.wysiwyg.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.security.management
import zope.security.proxy
import zope.traversing.interfaces


class HTMLConverter(object):
    """General XML to HTML converter.

    This html converter doesn't operate on `context` and is registered for all
    objects. If a content object requires a more specialised adapter it can be
    registered easily.

    The actual conversion work is delegated to `ConversionStep`s which are
    registered as named adapters, and sorted by their weight
    (ascending for to_html() and descending for to_xml()).
    """

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.wysiwyg.interfaces.IHTMLConverter)

    editable_xml_nodes = frozenset(['p', 'intertitle', 'article_extra',
                                    'ul', 'ol', 'video', 'audio', 'raw'])

    def __init__(self, context):
        self.context = context

    def to_html(self, tree):
        """converts XML `tree` to HTML."""

        tree = zope.security.proxy.removeSecurityProxy(tree)
        # copy so the conversion steps can work in-place
        tree = self._copy(tree)
        self._apply_steps(tree, 'xpath_xml', 'to_html', reverse=False)

        result = []
        for child in tree.iterchildren():
            result.append(lxml.etree.tostring(
                copy.copy(child), pretty_print=True, encoding=unicode))
        return ''.join(result)

    def from_html(self, tree, value):
        """converts the HTML `value` to XML and sets it on `tree`."""

        tree = zope.security.proxy.removeSecurityProxy(tree)
        self._clear(tree)
        if not value:
            # We're done. Just don't do anything.
            return

        value = '<div>' + self._replace_entities(value) + '</div>'
        __traceback_info__ = (value,)
        html = lxml.objectify.fromstring(value)

        self._apply_steps(html, 'xpath_html', 'to_xml', reverse=True)
        for node in html.iterchildren():
            # copy to kill namespaces
            tree.append(copy.copy(node))

        zope.security.proxy.removeSecurityProxy(self.context)._p_changed = 1

    def _apply_steps(self, tree, xpath, method, reverse):
        steps = [adapter for name, adapter in zope.component.getAdapters(
                (self.context,), zeit.wysiwyg.interfaces.IConversionStep)]
        steps = sorted(steps, key=lambda x: x.weight, reverse=reverse)

        for adapter in steps:
            xp = getattr(adapter, xpath)
            if xp is SKIP:
                continue
            convert = getattr(adapter, method)
            for node in tree.xpath(xp):
                filtered = convert(node)
                if filtered is not None:
                    node.getparent().replace(node, filtered)
                    filtered.tail = node.tail

    def covered_xpath(self):
        """return an xpath query that matches all nodes for which there is a
        ConversionStep registered."""
        steps = [adapter for name, adapter in zope.component.getAdapters(
                (self.context,), zeit.wysiwyg.interfaces.IConversionStep)]
        xpath = [s.xpath_xml for s in steps
                 if s.xpath_xml is not SKIP and s.xpath_xml != '.']
        return '|'.join(xpath)

    def _copy(self, tree):
        """return a copy of `tree` that contains only those nodes we know how to
        deal with."""
        root = lxml.objectify.E.body()
        covered = tree.xpath(self.covered_xpath())
        for child in tree.iterchildren():
            if child in covered:
                root.append(copy.copy(child))
        return root

    def _clear(self, tree):
        """removes all nodes we want to edit from `tree`"""
        for node in tree.xpath(self.covered_xpath()):
            parent = node.getparent()
            parent.remove(node)

    @staticmethod
    def _replace_entities(value):
        # XXX is this efficient enough?
        for entity_name, codepoint in htmlentitydefs.name2codepoint.items():
            if entity_name in ('gt', 'lt', 'quot', 'amp', 'apos'):
                # don't replace XML built-in entities
                continue
            value = value.replace('&'+entity_name+';', unichr(codepoint))
        return value


SKIP = object()


class ConversionStep(object):
    """Encapsulates one step of XML<-->HTML conversion.

    to_html() is called with each XML node matching xpath_xml, while
    to_xml() is called with each HTML node matching xpath_html.
    They should work in-place, but can optionally return a value which will be
    used to replace the original node.

    The XPath is applied against the root node, so if you want to do special
    processing (such as dropping or rearranging nodes), use '.' to be called
    just once, with the root node.

    To specify the order in which the steps are applied, set their weight
    accordingly. The default is 0, and steps are sorted ascending for to_html()
    and descending for to_xml().

    The adapter context can be used to fine-tune for which objects a conversion
    step applies, but probably should not be touched for anything else. Remember
    to register steps as named adapters (the name itself doesn't matter), so the
    HTMLConverter can pick them all up using getAdapters().
    """

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.wysiwyg.interfaces.IConversionStep)
    weight = 0.0

    def __init__(self, context):
        self.context = context
        self.request = (
            zope.security.management.getInteraction().participations[0])

    # override in subclass
    xpath_xml = SKIP
    xpath_html = SKIP

    def to_html(self, node):
        raise NotImplementedError(
            "when specifiyng xpath_xml, to_html() must be implemented")

    def to_xml(self, node):
        raise NotImplementedError(
            "when specifiyng xpath_html, to_xml() must be implemented")

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def url(self, obj):
        return zope.component.getMultiAdapter(
            (obj, self.request), name='absolute_url')()


class DropEmptyStep(ConversionStep):
    """Drop empty HTML toplevel nodes."""

    weight = 1.0
    xpath_html = 'child::*'

    def to_xml(self, node):
        if not node.countchildren() and not node.text:
            node.getparent().remove(node)
        if node.text and not node.text.strip():
            node.getparent().remove(node)


class TagReplaceStep(ConversionStep):
    """Convert between XML tag names and HTML ones."""

    weight = 0.9
    xpath_html = './/*'

    xml_html_tags = {
        'intertitle': 'h3',
    }
    html_xml_tags = dict((value, key) for key, value in xml_html_tags.items())
    assert len(html_xml_tags) == len(xml_html_tags)

    def __init__(self, context):
        super(TagReplaceStep, self).__init__(context)
        self.xpath_xml = '|'.join(['.//%s' % tag for tag
                                   in self.xml_html_tags.keys()])

    def to_html(self, node):
        new_tag = self.xml_html_tags.get(node.tag)
        if new_tag is not None:
            node.tag = new_tag

    def to_xml(self, node):
        new_tag = self.html_xml_tags.get(node.tag)
        if new_tag is not None:
            node.tag = new_tag


class PassThroughStep(ConversionStep):
    """Allow some XML tags to pass through to HTML.

    This adapter exists only for the side effect of making its xpath_xml
    known to HTMLConverter.covered_xpath()
    """

    allow_tags = ['p', 'ul', 'ol']

    def __init__(self, context):
        super(PassThroughStep, self).__init__(context)
        self.xpath_xml = '|'.join(['.//%s' % tag for tag in self.allow_tags])

    def to_html(self, node):
        pass


class TableStep(ConversionStep):
    """Clean up <table>s.
    """

    xpath_xml = './/table'
    xpath_html = './/table'

    def to_html(self, node):
        pass

    def to_xml(self, node):
        for name in node.attrib:
            del node.attrib[name]


class NormalizeToplevelStep(ConversionStep):
    """Normalize any toplevel tag we don't have a ConversionStep for to <p>."""

    weight = -1.0
    xpath_html = '.'

    def to_xml(self, node):
        # XXX having to go back to the HTMLConverter is a little kludgy
        converter = zeit.wysiwyg.interfaces.IHTMLConverter(self.context)
        xpath = converter.covered_xpath()
        covered = node.xpath(xpath)
        for child in node.iterchildren():
            if child not in covered:
                child.tag = 'p'


class NestedParagraphsStep(ConversionStep):
    """Un-nest nested <p>s."""

    weight = -1.0
    xpath_html = 'child::p'

    def to_xml(self, node):
        p_nodes = node.xpath('p')
        parent_index = node.getparent().index(node)
        for i, insert in enumerate(p_nodes):
            node.getparent().insert(parent_index+i+1, insert)
        if p_nodes:
            node.getparent().remove(node)


class ImageStep(ConversionStep):
    """Replace XML <image/> by HTML <img/> and vice versa."""

    xpath_xml = './/image'
    xpath_html = './/img'

    def to_html(self, node):
        unique_id = node.get('src')
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

        return lxml.objectify.E.img(src=url)

    def to_xml(self, node):
        repository_url = self.url(self.repository)
        url = node.get('src')

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
        return new_node


class URLStep(ConversionStep):
    """Convert uniqueIds to clickable CMS-URLs and vice versa."""

    xpath_xml = './/a'
    xpath_html = './/a'

    def _id_to_url(self, id):
        try:
            obj = self.repository.getContent(id)
        except (KeyError, ValueError):
            return id
        return self.url(obj)

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

    def to_html(self, node):
        id = node.get('href')
        if id:
            node.set('href', self._id_to_url(id))

    def to_xml(self, node):
        url = node.get('href')
        if url:
            node.set('href', self._url_to_id(url))


class ArticleExtraStep(ConversionStep):
    """Make <article_extra> editable."""

    weight = -0.1 # before VideoAudio

    xpath_xml = './/article_extra'
    xpath_html = './/p'

    def to_html(self, node):
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

    def to_xml(self, node):
        if node.find('input') is None:
            return

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

        new_node = lxml.objectify.E.article_extra()
        invalid_counter = 0
        for key, value in data.items():
            try:
                new_node.set(key, value)
            except ValueError:
                # Key is not a valid attribute name.
                invalid_counter += 1
                new_node.set('invalid%s' % invalid_counter,
                             '%s=%s' % (key, value))
        return new_node


class VideoAudioStep(ConversionStep):
    """Make <video> and <audio> editable."""

    xpath_xml = './/video|.//audio'
    xpath_html = './/*[@class="video" or @class="audio"]'

    def to_html(self, node):
        if node.tag == 'video':
            id_ = node.get('videoID')
            id_class = 'videoId'
            div_class = 'video'
        elif node.tag == 'audio':
            id_ = node.get('audioID')
            id_class = 'audioId'
            div_class = 'audio'

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

        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(id_, **{'class': id_class}),
            lxml.objectify.E.div(expires, **{'class': 'expires'}),
            lxml.objectify.E.div(format, **{'class': 'format'}),
            **{'class': div_class})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        if node.get('class') == 'video':
            id_nodes = node.xpath('div[@class="videoId"]')
            video = True
        elif node.get('class') == 'audio':
            id_nodes = node.xpath('div[@class="audioId"]')
            video = False

        id_ = expires = format = ''
        if id_nodes:
            id_ = unicode(id_nodes[0])
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
                expires = tz.localize(expires).isoformat()
        nodes = node.xpath('div[@class="format"]')
        if nodes:
            format = unicode(nodes[0])
        if video:
            new_node = lxml.objectify.E.video(videoID=id_, expires=expires,
                                              format=format)
        else:
            new_node = lxml.objectify.E.audio(audioID=id_, expires=expires,
                                              format=format)
        return new_node


class RawXMLStep(ConversionStep):
    """Make <raw> editable."""

    xpath_xml = './/raw'
    xpath_html = './/*[@class="raw"]'

    def to_html(self, node):
        result = []
        for child in node.iterchildren():
            # kill namespaces
            child = copy.copy(child)
            result.append(
                lxml.etree.tostring(child, pretty_print=True, encoding=unicode))
        text = '\n'.join(result)
        new_node = lxml.objectify.E.div(text, **{'class': 'raw'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        # must only contain text, everything else will be discarded
        text = xml.sax.saxutils.unescape(node.text)
        new_node = lxml.objectify.fromstring('<raw>%s</raw>' % node.text)
        return new_node


class ReferenceStep(ConversionStep):

    content_type = None # override in subclass

    def __init__(self, context):
        super(ReferenceStep, self).__init__(context)
        self.xpath_xml = './/%s' % self.content_type
        self.xpath_html = './/*[@class="%s"]' % self.content_type

    def to_html(self, node):
        content = zeit.cms.interfaces.ICMSContent(node.get('href'))
        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(self.url(content), **{'class': 'href'}),
            **{'class': self.content_type})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        url = node.xpath('*[@class="href"]')[0].text
        repository_url = self.url(self.repository) + '/'
        unique_id = url.replace(
            repository_url, zeit.cms.interfaces.ID_NAMESPACE)

        factory = getattr(lxml.objectify.E, self.content_type)
        new_node = factory(href=unique_id)
        content = zeit.cms.interfaces.ICMSContent(unique_id)
        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(content)
        updater.update(new_node)
        return new_node


class PortraitboxStep(ReferenceStep):

    content_type = 'portraitbox'


class InfoboxStep(ReferenceStep):

    content_type = 'infobox'


class GalleryStep(ReferenceStep):

    content_type = 'gallery'


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
