# coding: utf8
# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.util import objectify_soup_fromstring
from zeit.wysiwyg.util import contains_element
import copy
import datetime
import htmlentitydefs
import lxml.etree
import lxml.objectify
import rwproperty
import time
import zc.iso8601.parse
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
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

    def _steps(self, reverse=False):
        steps = [adapter for name, adapter in zope.component.getAdapters(
                (self.context,), zeit.wysiwyg.interfaces.IConversionStep)]
        steps = sorted(steps, key=lambda x: x.weight, reverse=reverse)
        return steps

    def _apply_steps(self, tree, xpath, method, reverse):
        for adapter in self._steps(reverse):
            xp = getattr(adapter, xpath)
            if xp is SKIP:
                continue
            convert = getattr(adapter, method)
            for node in tree.xpath(xp):
                filtered = convert(node)
                if filtered is not None:
                    node.getparent().replace(node, filtered)
                    filtered.tail = node.tail

    def references(self, tree):
        return self._retrieve_content(self._extract_referenced_ids(tree))

    def _extract_referenced_ids(self, tree):
        result = []
        tree = zope.security.proxy.removeSecurityProxy(tree)
        for adapter in self._steps():
            xp = getattr(adapter, 'xpath_xml')
            if xp is SKIP:
                continue
            for node in tree.xpath(xp):
                result.extend(adapter.references(node))
        return result

    def _retrieve_content(self, ids):
        result = []
        for id in ids:
            if not id.startswith(zeit.cms.interfaces.ID_NAMESPACE):
                continue
            obj = zeit.cms.interfaces.ICMSContent(id, None)
            if obj is not None:
                result.append(obj)
        return result

    def covered_xpath(self):
        """return an xpath query that matches all nodes for which there is a
        ConversionStep registered."""
        xpath = [s.xpath_xml for s in self._steps()
                 if s.xpath_xml is not SKIP and s.xpath_xml != '.']
        return '|'.join(xpath)

    def _copy(self, tree):
        """return a copy of `tree` that contains only those nodes we know how
        to deal with."""
        root = lxml.objectify.E.body()
        xpath = self.covered_xpath()
        if not xpath:
            return root
        covered = tree.xpath(xpath)
        for child in tree.iterchildren():
            if contains_element(covered, child):
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
    step applies, but probably should not be touched for anything else.
    Remember to register steps as named adapters (the name itself doesn't
    matter), so the HTMLConverter can pick them all up using getAdapters().
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

    def references(self, node):
        return []

    @zope.cachedescriptors.property.Lazy
    def repository(self):
        return zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)

    def url(self, obj):
        return zope.component.getMultiAdapter(
            (obj, self.request), name='absolute_url')()

    def datetime_to_html(self, dt_string):
        dt = ''
        if dt_string:
            try:
                dt = zc.iso8601.parse.datetimetz(dt_string)
            except ValueError:
                pass
            else:
                tz = zope.interface.common.idatetime.ITZInfo(self.request)
                dt = dt.astimezone(tz).strftime('%Y-%m-%d %H:%M')
        return dt

    def datetime_to_xml(self, dt_string):
        dt = ''
        if dt_string:
            try:
                dt = datetime.datetime.strptime(dt_string, '%Y-%m-%d %H:%M')
            except ValueError:
                dt = ''
            else:
                tz = zope.interface.common.idatetime.ITZInfo(self.request)
                dt = tz.localize(dt).isoformat()
        return dt


class DropEmptyStep(ConversionStep):
    """Drop empty HTML toplevel nodes."""

    weight = 1.0
    xpath_html = 'child::*'

    def to_xml(self, node):
        if node.get('keep'):
            del node.attrib['keep']
            return
        if node.countchildren():
            return
        if node.text and node.text.strip():
            return
        if node.attrib:
            return
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
        unique_id = node.get('src', '')
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

        img = lxml.objectify.E.img()
        if url:
            img.set('src', url)
        layout = node.get('layout')
        if layout:
            img.set('title', layout)
        return img

    def to_xml(self, node):
        repository_url = self.url(self.repository)
        url = node.get('src')

        new_node = None
        if url and url.startswith(repository_url):
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
            # An XML reference could not be created because the object could
            # not be found. Instead of just removing the image we create an
            # image tag with the url we've got. This way it is also possible to
            # create images to other servers.
            new_node = lxml.objectify.E.image()
            if url:
                new_node.set('src', url)
        layout = node.get('title')
        if layout:
            new_node.set('layout', layout)
        return new_node

    def references(self, node):
        unique_id = node.get('src', '')
        return [unique_id]


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


class AudioStep(ConversionStep):
    """Make editable."""

    xpath_xml = './/audio'
    xpath_html = ('.//*[contains(@class, "inline-element") and '
                  'contains(@class, "audio")]')

    def to_html(self, node):
        id_ = node.get('audioID')
        expires = self.datetime_to_html(node.get('expires'))
        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(id_, **{'class': 'audioId'}),
            lxml.objectify.E.div(expires, **{'class': 'expires'}),
            **{'class': 'inline-element audio'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        id_nodes = node.xpath('div[@class="audioId"]')

        id_ = expires = ''
        if id_nodes:
            id_ = unicode(id_nodes[0])

        nodes = node.xpath('div[@class="expires"]')
        if nodes:
            expires = self.datetime_to_xml(unicode(nodes[0]))
        new_node = lxml.objectify.E.audio(audioID=id_, expires=expires)
        return new_node


class VideoStep(ConversionStep):
    """Make <video> editable."""

    xpath_xml = './/video'
    xpath_html = ('.//*[contains(@class, "inline-element") and '
                  'contains(@class, "video")]')

    def to_html(self, node):
        id_1 = node.get('videoID', '')
        id_2 = node.get('videoID2', '')
        player_1 = 'playlist' if node.get('player') == 'pls' else 'video'
        player_2 = 'playlist' if node.get('player2') == 'pls' else 'video'
        if id_1:
            id_1 = 'http://video.zeit.de/%s/%s' % (player_1, id_1)
        if id_2:
            id_2 = 'http://video.zeit.de/%s/%s' % (player_2, id_2)
        expires = self.datetime_to_html(node.get('expires'))
        format = node.get('format') or ''

        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(id_1, **{'class': 'videoId'}),
            lxml.objectify.E.div(id_2, **{'class': 'videoId2'}),
            lxml.objectify.E.div(expires, **{'class': 'expires'}),
            lxml.objectify.E.div(format, **{'class': 'format'}),
            **{'class': 'inline-element video'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        id_nodes = node.xpath('div[contains(@class, "videoId")]')
        id_ = id2 = expires = format = ''
        if id_nodes:
            id_ = unicode(id_nodes[0])
            if len(id_nodes) > 1:
                id2 = unicode(id_nodes[1])

        nodes = node.xpath('div[@class="expires"]')
        if nodes:
            user_expires = self.datetime_to_xml(unicode(nodes[0]))
        else:
            user_expires = None
        expires = self._expires(id_, id2, user_expires)

        def get_id_player(video_id):
            if video_id and video_id.startswith('http://video.zeit.de/'):
                video_id = video_id.replace('http://video.zeit.de/', '', 1)
                if '/' in video_id:
                    type_, id_ = video_id.split('/', 1)
                    type_ = 'pls' if type_ == 'playlist' else 'vid'
                    return id_, type_
            return '', ''

        id_, p1 = get_id_player(id_)
        id2, p2 = get_id_player(id2)

        nodes = node.xpath('div[@class="format"]')
        if nodes:
            format = unicode(nodes[0])
        new_node = lxml.objectify.E.video(
            videoID=id_, videoID2=id2, expires=expires, format=format,
            player=p1, player2=p2)
        return new_node

    def _expires(self, video1, video2, user_entered):
        if user_entered:
            return user_entered

        all_expires = []
        maximum = datetime.datetime(datetime.MAXYEAR, 12, 31)
        for id in [video1, video2]:
            video = zeit.cms.interfaces.ICMSContent(id, None)
            expires = getattr(video, 'expires', maximum)
            all_expires.append(expires)
        expires = min(all_expires)
        if expires == maximum:
            return ''

        tz = zope.interface.common.idatetime.ITZInfo(self.request)
        return tz.localize(expires).isoformat()


class RawXMLStep(ConversionStep):
    """Make <raw> editable."""

    xpath_xml = './/raw'
    xpath_html = './/*[contains(@class, "raw")]'

    def to_html(self, node):
        result = []
        for child in node.iterchildren():
            # kill namespaces
            child = copy.copy(child)
            result.append(lxml.etree.tostring(
                child, pretty_print=True, encoding=unicode))
        text = '\n'.join(result)
        new_node = lxml.objectify.E.div(
            text, **{'class': 'inline-element raw'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        new_node = objectify_soup_fromstring('<raw>%s</raw>' % node.text)
        return new_node


class ReferenceStep(ConversionStep):
    """"""

    content_type = None # override in subclass

    def __init__(self, context):
        super(ReferenceStep, self).__init__(context)
        self.xpath_xml = './/%s' % self.content_type
        self.xpath_html = './/*[contains(@class, "%s")]' % self.content_type

    def to_html(self, node):
        href = node.get('href')
        new_node = lxml.objectify.E.div(
            lxml.objectify.E.div(href, **{'class': 'href'}),
            **{'class': 'inline-element %s' % self.content_type})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        unique_id = node.xpath('*[contains(@class, "href")]')[0].text

        factory = getattr(lxml.objectify.E, self.content_type)
        new_node = factory(href=unique_id)
        content = zeit.cms.interfaces.ICMSContent(unique_id, None)
        if content is not None:
            updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(content)
            updater.update(new_node)
        return new_node

    def references(self, node):
        unique_id = node.get('href')
        return [unique_id]


class PortraitboxStep(ReferenceStep):

    content_type = 'portraitbox'

    def to_html(self, node):
        new_node = super(PortraitboxStep, self).to_html(node)
        layout = lxml.objectify.E.div(
            node.get('layout'), **{'class': 'layout'})
        lxml.objectify.deannotate(layout)
        new_node.append(layout)
        return new_node

    def to_xml(self, node):
        new_node = super(PortraitboxStep, self).to_xml(node)
        layout = node.xpath('*[@class="layout"]')[0].text
        new_node.set('layout', layout)
        return new_node


class InfoboxStep(ReferenceStep):

    content_type = 'infobox'


class GalleryStep(ReferenceStep):

    content_type = 'gallery'


class CitationStep(ConversionStep):

    attributes = ['text', 'text2',
                  'attribution', 'attribution2',
                  'url', 'url2',
                  'layout']

    xpath_xml = './/citation'
    xpath_html = './/*[contains(@class, "citation")]'

    def to_html(self, node):
        children = []
        for name in self.attributes:
            children.append(lxml.objectify.E.div(
                node.get(name), **{'class': name}))
        new_node = lxml.objectify.E.div(
            *children, **{'class': 'inline-element citation'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        values = {}
        for name in self.attributes:
            value = node.xpath('*[@class="%s"]' % name)[0].text
            values[name] = value
        new_node = lxml.objectify.E.citation(**values)
        return new_node


class RelatedsStep(ConversionStep):

    xpath_xml = './/relateds'
    xpath_html = './/*[contains(@class, "relateds")]'
    weight = +1.5

    def to_html(self, node):
        new_node = lxml.objectify.E.div(
            ' ', **{'class': 'inline-element relateds'})
        lxml.objectify.deannotate(new_node)
        return new_node

    def to_xml(self, node):
        return lxml.objectify.E.relateds(keep='yes')


class InlineElementAppendParagraph(ConversionStep):
    """Add an empty paragraph after each inline element.

    This is necessary to allow to position the cursor between two blocks.
    The empty paragraph stripper will remove those paragraphs when converting
    to XML.

    """

    weight = 100
    xpath_xml = './/*[contains(@class, "inline-element")]'

    def to_html(self, node):
        index = node.getparent().index(node)
        # Note: between the ' ' there is a non-breaking space.
        p = lxml.objectify.E.p(u' ')
        lxml.objectify.deannotate(p)
        node.getparent().insert(index + 1, p)
        return node


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
    def references(self):
        return self.convert.references(self.get_tree())

    @property
    def convert(self):
        return zeit.wysiwyg.interfaces.IHTMLConverter(self.context)

    def get_tree(self):
        raise NotImplementedError("Implemented in subclass.")
