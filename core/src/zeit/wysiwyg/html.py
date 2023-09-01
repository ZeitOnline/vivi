# coding: utf8
from zeit.wysiwyg.util import contains_element
import copy
import datetime
import html.entities
import lxml.builder
import lxml.etree
import lxml.html.soupparser
import lxml.objectify
import pendulum
import pytz
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


@zope.component.adapter(zope.interface.Interface)
@zope.interface.implementer(zeit.wysiwyg.interfaces.IHTMLConverter)
class HTMLConverter:
    """General XML to HTML converter.

    This html converter doesn't operate on `context` and is registered for all
    objects. If a content object requires a more specialised adapter it can be
    registered easily.

    The actual conversion work is delegated to `ConversionStep`s which are
    registered as named adapters, and sorted by their order specific to the
    conversion direction.

    """

    def __init__(self, context):
        self.context = context
        self.storage = {}

    def to_html(self, tree):
        """converts XML `tree` to HTML."""

        tree = zope.security.proxy.removeSecurityProxy(tree)
        # copy so the conversion steps can work in-place
        tree = self._copy(tree)
        self._apply_steps(tree, 'xpath_xml', 'to_html')

        result = []
        for child in tree.iterchildren():
            result.append(lxml.etree.tostring(
                child, pretty_print=True, encoding=str))
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
        html = lxml.etree.fromstring(value)

        self._apply_steps(html, 'xpath_html', 'to_xml')
        for node in html.iterchildren():
            # support tails at the toplevel by faking a wrapper node
            xml = '<foo>%s</foo>' % lxml.etree.tostring(node, encoding=str)
            objectified = lxml.objectify.fromstring(xml)
            for child in objectified.iterchildren():
                tree.append(child)

        zope.security.proxy.removeSecurityProxy(self.context)._p_changed = 1

    def _steps(self, direction):
        steps = [adapter for name, adapter in zope.component.getAdapters(
            (self.context, self), zeit.wysiwyg.interfaces.IConversionStep)]
        steps = sorted(steps, key=lambda x: getattr(x, 'order_' + direction))
        return steps

    def _apply_steps(self, tree, xpath, method):
        for adapter in self._steps(direction=method):
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
        for adapter in self._steps('to_html'):
            xp = adapter.xpath_xml
            if xp is SKIP:
                continue
            for node in tree.xpath(xp):
                result.extend(adapter.references(node))
        return result

    def _retrieve_content(self, ids):
        result = []
        for id in ids:
            if not id:
                continue
            if not id.startswith(zeit.cms.interfaces.ID_NAMESPACE):
                continue
            obj = zeit.cms.interfaces.ICMSContent(id, None)
            if obj is not None:
                result.append(obj)
        return result

    def covered_xpath(self):
        """return an xpath query that matches all nodes for which there is a
        ConversionStep registered."""
        xpath = [s.xpath_xml for s in self._steps('to_html')
                 if s.xpath_xml is not SKIP and s.xpath_xml != '.']
        return '|'.join(xpath)

    def _copy(self, tree):
        """return a copy of `tree` that contains only those nodes we know how
        to deal with."""
        root = lxml.builder.E.body()
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
        for entity_name, codepoint in html.entities.name2codepoint.items():
            if entity_name in ('gt', 'lt', 'quot', 'amp', 'apos'):
                # don't replace XML built-in entities
                continue
            value = value.replace('&' + entity_name + ';', chr(codepoint))
        return value


SKIP = object()


@zope.component.adapter(
    zope.interface.Interface, zeit.wysiwyg.interfaces.IHTMLConverter)
@zope.interface.implementer(zeit.wysiwyg.interfaces.IConversionStep)
class ConversionStep:
    """Encapsulates one step of XML<-->HTML conversion.

    to_html() is called with each XML node matching xpath_xml, while
    to_xml() is called with each HTML node matching xpath_html.
    They should work in-place, but can optionally return a value which will be
    used to replace the original node.

    The XPath is applied against the root node, so if you want to do special
    processing (such as dropping or rearranging nodes), use '.' to be called
    just once, with the root node.

    To specify the order in which the steps are applied, set their orders
    specific to the conversion direction.

    The adapter context can be used to fine-tune for which objects a conversion
    step applies, but probably should not be touched for anything else.
    Remember to register steps as named adapters (the name itself doesn't
    matter), so the HTMLConverter can pick them all up using getAdapters().
    """

    order_to_html = 0.0
    order_to_xml = 0.0

    def __init__(self, context, converter):
        self.context = context
        self.converter = converter
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
                dt = pendulum.parse(dt_string)
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

    order_to_xml = -1.0
    xpath_html = 'child::*'

    def to_xml(self, node):
        if node.get('keep'):
            del node.attrib['keep']
            return
        if len(node):
            return
        if node.text and node.text.strip():
            return
        if node.attrib:
            return
        node.getparent().remove(node)


class TagReplaceStep(ConversionStep):
    """Convert between XML tag names and HTML ones."""

    order_to_html = 0.9
    order_to_xml = -0.9
    xpath_html = './/*'

    xml_html_tags = {
        'intertitle': 'h3',
    }
    html_xml_tags = {value: key for key, value in xml_html_tags.items()}
    assert len(html_xml_tags) == len(xml_html_tags)

    def __init__(self, context, converter):
        super().__init__(context, converter)
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

    def __init__(self, context, converter):
        super().__init__(context, converter)
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


ContentOnlyElements = (
    lxml.etree._Comment, lxml.etree._ProcessingInstruction, lxml.etree._Entity)


class NormalizeToplevelStep(ConversionStep):
    """Normalize any toplevel tag we don't have a ConversionStep for to <p>."""

    order_to_xml = 1.0
    xpath_html = '.'

    def to_xml(self, node):
        # XXX having to go back to the HTMLConverter is a little kludgy
        xpath = self.converter.covered_xpath()
        covered = node.xpath(xpath)
        for child in node.iterchildren():
            if isinstance(child, ContentOnlyElements):
                continue
            if child not in covered:
                child.tag = 'p'


class NestedParagraphsStep(ConversionStep):
    """Un-nest nested <p>s."""

    order_to_xml = 1.0
    xpath_html = 'child::p'

    def to_xml(self, node):
        p_nodes = node.xpath('p')
        parent_index = node.getparent().index(node)
        for i, insert in enumerate(p_nodes):
            node.getparent().insert(parent_index + i + 1, insert)
        if p_nodes:
            node.getparent().remove(node)


class ImageStructureStep(ConversionStep):

    def _convert(self, node):
        # Hacky support for linked images (#10033)
        if node.getparent().tag == 'a':
            return

        if node.tail:
            if node.getprevious() is not None:
                self.append_or_set(node.getprevious(), 'tail', node.tail)
            else:
                self.append_or_set(node.getparent(), 'text', node.tail)
            node.tail = None

        body = node
        insert_before = None
        while not self._is_root(body, node):
            insert_before = body
            body = body.getparent()
        insert_before.addprevious(node)

    def append_or_set(self, node, property, value):
        current_value = getattr(node, property)
        if current_value is not None:
            value = current_value + value
        setattr(node, property, value)

    def _is_root(self, element, orig_node):
        raise NotImplementedError('override in subclass')


class HTMLImageStructureStep(ImageStructureStep):

    xpath_html = './*//img'
    order_to_xml = -2

    def to_xml(self, node):
        return self._convert(node)

    def _is_root(self, element, orig_node):
        return element == orig_node.getroottree().getroot()


class XMLImageStructureStep(ImageStructureStep):

    xpath_xml = './*//image'
    order_to_html = -2

    def to_html(self, node):
        return self._convert(node)

    def _is_root(self, element, orig_node):
        return element.tag == 'body'


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
                url = self.url(image) + '/@@raw'

        img = lxml.builder.E.img()
        if url:
            img.set('src', url)
        layout = node.get('layout')
        if layout:
            img.set('title', layout)
        new_node = img
        if node.getparent().tag != 'a':
            # wrap in a <p> so html is happy
            new_node = lxml.builder.E.p(img)
        return new_node

    def to_xml(self, node):
        repository_url = self.url(self.repository) + '/'
        url = node.get('src')

        new_node = None
        if url and url.startswith(repository_url):
            unique_id = url.replace(
                repository_url, zeit.cms.interfaces.ID_NAMESPACE, 1).replace(
                    '/@@raw', '')
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
            new_node = lxml.builder.E.image()
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
        path = url[len(repository_url) + 1:]
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
        new_node = lxml.builder.E.div(
            lxml.builder.E.div(id_, **{'class': 'audioId'}),
            lxml.builder.E.div(expires, **{'class': 'expires'}),
            **{'class': 'inline-element audio'})
        return new_node

    def to_xml(self, node):
        id_nodes = node.xpath('div[@class="audioId"]')

        id_ = expires = ''
        if id_nodes:
            id_ = id_nodes[0].text

        nodes = node.xpath('div[@class="expires"]')
        if nodes:
            expires = self.datetime_to_xml(nodes[0].text)
        new_node = lxml.builder.E.audio(audioID=id_, expires=expires)
        return new_node


class VideoStep(ConversionStep):
    """Make <video> editable."""

    xpath_xml = './/video'
    xpath_html = ('.//*[contains(@class, "inline-element") and '
                  'contains(@class, "video")]')

    def to_html(self, node):
        id1 = node.get('href') or ''
        id2 = node.get('href2') or ''
        expires = self.datetime_to_html(node.get('expires'))
        format = node.get('format') or ''

        new_node = lxml.builder.E.div(
            lxml.builder.E.div(id1, **{'class': 'videoId'}),
            lxml.builder.E.div(id2, **{'class': 'videoId2'}),
            lxml.builder.E.div(expires, **{'class': 'expires'}),
            lxml.builder.E.div(format, **{'class': 'format'}),
            **{'class': 'inline-element video'})
        return new_node

    def to_xml(self, node):
        id_nodes = node.xpath('div[contains(@class, "videoId")]')
        id1 = id2 = expires = format = ''
        if id_nodes:
            id1 = id_nodes[0].text
            if len(id_nodes) > 1:
                id2 = id_nodes[1].text

        nodes = node.xpath('div[@class="expires"]')
        if nodes:
            user_expires = self.datetime_to_xml(nodes[0].text)
        else:
            user_expires = None
        expires = self._expires(id1, id2, user_expires)

        def get_id_player(video_id):
            if video_id and video_id.startswith('http://video.zeit.de/'):
                video_id = video_id.replace('http://video.zeit.de/', '', 1)
                if '/' in video_id:
                    type_, id_ = video_id.split('/', 1)
                    type_ = 'pls' if type_ == 'playlist' else 'vid'
                    return id_, type_
            return '', ''

        old_id, player1 = get_id_player(id1)
        old_id2, player2 = get_id_player(id2)

        nodes = node.xpath('div[@class="format"]')
        if nodes:
            format = nodes[0].text or ''
        new_node = lxml.builder.E.video(
            href=id1 or '', href2=id2 or '',
            expires=expires, format=format)
        return new_node

    # XXX duplicated code in zeit.brightcove.asset
    def _expires(self, video1, video2, user_entered):
        """returns the earliest expire date of the two objects (the
        user-entered value takes precedence)"""

        if user_entered:
            return user_entered

        # an expires value might
        # - not exist on the object (if it's a Playlist)
        # - exist but be None (if a Video doesn't expire)
        all_expires = []
        maximum = datetime.datetime(datetime.MAXYEAR, 12, 31, tzinfo=pytz.UTC)
        for id in [video1, video2]:
            video = zeit.cms.interfaces.ICMSContent(id, None)
            expires = getattr(video, 'expires', None)
            if expires is None:
                expires = maximum
            all_expires.append(expires)
        expires = min(all_expires)
        if expires == maximum:
            return ''

        return expires.isoformat()


class RawXMLProtectStep(ConversionStep):
    """Contents of <raw> must not be subjected to any other conversion steps.
    """

    order_to_html = -50
    order_to_xml = -50
    xpath_xml = './/raw'
    xpath_html = './/*[contains(@class, "raw")]'

    def to_html(self, node):
        self.store(node)
        return node

    def to_xml(self, node):
        self.store(node)
        return node

    def store(self, node):
        storage = self.converter.storage.setdefault('raw', {})
        children = storage[node] = list(node.iterchildren())
        for child in children:
            node.remove(child)


class RawXMLUnprotectStep(ConversionStep):
    """Contents of <raw> must not be subjected to any other conversion steps.
    """

    order_to_html = 50
    order_to_xml = 50
    xpath_xml = './/raw'
    xpath_html = './/*[contains(@class, "raw")]'

    def to_html(self, node):
        self.restore(node)
        return node

    def to_xml(self, node):
        self.restore(node)
        return node

    def restore(self, node):
        storage = self.converter.storage.setdefault('raw', {})
        for child in storage[node]:
            node.append(child)


class RawXMLStep(ConversionStep):
    """Make <raw> editable."""

    order_to_html = 51
    order_to_xml = 51
    xpath_xml = './/raw'
    xpath_html = './/*[contains(@class, "raw")]'

    def to_html(self, node):
        result = []
        for child in node.iterchildren():
            result.append(lxml.etree.tostring(
                child, pretty_print=True, encoding=str))
        text = '\n'.join(result)
        new_node = lxml.builder.E.div(
            text, **{'class': 'inline-element raw'})
        return new_node

    def to_xml(self, node):
        new_node = lxml.html.soupparser.fromstring(node.text)
        new_node.tag = 'raw'
        return new_node


class ReferenceStep(ConversionStep):

    content_type = None  # override in subclass

    def __init__(self, context, converter):
        super().__init__(context, converter)
        self.xpath_xml = './/%s' % self.content_type
        self.xpath_html = './/*[contains(@class, "%s")]' % self.content_type

    def to_html(self, node):
        href = node.get('href') or ''
        new_node = lxml.builder.E.div(
            lxml.builder.E.div(href, **{'class': 'href'}),
            **{'class': 'inline-element %s' % self.content_type})
        return new_node

    def to_xml(self, node):
        unique_id = node.xpath('*[contains(@class, "href")]')[0].text or ''

        # Some metadata may be None, which objectify accepts for creating child
        # nodes, but etree doesn't. Fortunately, etree doesn't mind smuggling
        # in an objectify node here.
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
        new_node = super().to_html(node)
        layout = lxml.builder.E.div(
            node.get('layout') or '', **{'class': 'layout'})
        new_node.append(layout)
        return new_node

    def to_xml(self, node):
        new_node = super().to_xml(node)
        layout = node.xpath('*[@class="layout"]')[0].text or ''
        new_node.set('layout', layout)
        return new_node


class InfoboxStep(ReferenceStep):

    content_type = 'infobox'


class TimelineStep(ReferenceStep):

    content_type = 'timeline'


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
            children.append(lxml.builder.E.div(
                node.get(name) or ' ', **{'class': name}))
        new_node = lxml.builder.E.div(
            *children, **{'class': 'inline-element citation'})
        return new_node

    def to_xml(self, node):
        values = {}
        for name in self.attributes:
            value = node.xpath('*[@class="%s"]' % name)[0].text
            if value and value.strip():
                values[name] = value.strip()
        new_node = lxml.builder.E.citation(**values)
        return new_node


class InlineElementAppendParagraph(ConversionStep):
    """Add an empty paragraph after each inline element.

    This is necessary to allow to position the cursor between two blocks.
    The empty paragraph stripper will remove those paragraphs when converting
    to XML.

    """

    order_to_html = 100
    xpath_xml = './/*[contains(@class, "inline-element")]'

    def to_html(self, node):
        index = node.getparent().index(node)
        # Note: between the ' ' there is a non-breaking space.
        p = lxml.builder.E.p(' ')
        node.getparent().insert(index + 1, p)
        return node


@zope.interface.implementer(zeit.wysiwyg.interfaces.IHTMLContent)
class HTMLContentBase:
    """Base class for html content."""

    def __init__(self, context):
        self.context = context

    @property
    def html(self):
        return self.convert.to_html(self.get_tree())

    @html.setter
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
