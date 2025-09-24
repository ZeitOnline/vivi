import grokcore.component as grok
import lxml.etree
import zope.interface

import zeit.cms.content.interfaces
import zeit.connector.interfaces
import zeit.content.link.interfaces


class IRSSLink(zeit.content.link.interfaces.ILink):
    image_url = zope.interface.Attribute('image_url')


@zope.interface.implementer(IRSSLink)
class RSSLink:
    def __init__(self, feed, item):
        # Conform to ILink/IXMLContent, mostly for zeit.web
        self.xml = lxml.etree.Element('empty')

        self.__name__ = None
        self.__parent__ = None
        self.feed = feed

        parse = getattr(self, f'_parse_{feed.kind}')
        parse(item)

        self.teaserTitle = self.title
        self.teaserSupertitle = self.supertitle
        self.teaserText = self.text

        self.uniqueId = self.url

    def _parse_rss(self, xml):
        self.title = xml.findtext('title', '').strip()
        self.supertitle = xml.findtext('category', '').strip()
        self.text = xml.findtext('description')
        self.url = xml.findtext('link', '').strip()
        enclosure = xml.find('enclosure')
        self.image_url = enclosure.get('url') if enclosure is not None else None
        dc_type = xml.findtext('dc:type', namespaces={'dc': 'http://purl.org/dc/elements/1.1/'})
        self.is_ad = dc_type == 'native-ad'

    def _parse_wiwojson(self, item):
        teaser = item.get('teaser', {})
        self.title = teaser.get('headline', '').strip()
        self.supertitle = teaser.get('kicker', '').strip()
        self.text = teaser.get('leadText')
        self.url = item.get('link', '').strip()
        for img in teaser.get('image', {}).get('crops', ()):
            if img.get('name') == 'original':
                self.image_url = img.get('url')
        self.is_ad = False

    # Since only a few attributes of z.c.link.ILink are implemented,
    # fall back to the missing values of zopes schema fields
    def __getattr__(self, name):
        field = IRSSLink.get(name)
        if not field:
            raise AttributeError(name)
        return field.missing_value

    authorships = ()

    target = '_blank'


@grok.adapter(IRSSLink)
@grok.implementer(zeit.cms.content.interfaces.IUUID)
def no_uuid(context):
    return None


@grok.adapter(IRSSLink)
@grok.implementer(zeit.connector.interfaces.IWebDAVProperties)
def no_dav_props(context):
    return {}
