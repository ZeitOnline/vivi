# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import zope.interface

import zeit.cms.content.interfaces
import zeit.connector.interfaces
import zeit.content.link.interfaces


class IRSSLink(zeit.content.link.interfaces.ILink):
    image_url = zope.interface.Attribute('image_url')


@zope.interface.implementer(IRSSLink)
class RSSLink:
    def __init__(self, xml, feed=None):
        self.xml = xml
        self.__name__ = None
        self.__parent__ = None
        self.feed = feed
        self.uniqueId = self.url

    # Since only a few attributes of z.c.link.ILink are implemented,
    # fall back to the missing values of zopes schema fields
    def __getattr__(self, name):
        field = IRSSLink.get(name)
        if not field:
            raise AttributeError(name)
        return field.missing_value

    authorships = ()

    target = '_blank'

    @cachedproperty
    def title(self):
        title = self.xml.findtext('title')
        if title is None:
            return None
        return title.strip()

    @cachedproperty
    def teaserTitle(self):  # NOQA
        return self.title

    @cachedproperty
    def supertitle(self):
        supertitle = self.xml.findtext('category')
        if supertitle is None:
            return None
        return supertitle.strip()

    @cachedproperty
    def teaserSupertitle(self):  # NOQA
        return self.supertitle

    @cachedproperty
    def text(self):
        return self.xml.findtext('description')

    @cachedproperty
    def teaserText(self):  # NOQA
        return self.text

    @cachedproperty
    def url(self):
        link = self.xml.findtext('link')
        if link is None:
            return None
        return link.strip()

    @cachedproperty
    def image_url(self):
        enclosure = self.xml.find('enclosure')
        if enclosure is None:
            return None
        return enclosure.get('url')

    @cachedproperty
    def is_ad(self):
        dc_type = self.xml.find('dc:type', namespaces={'dc': 'http://purl.org/dc/elements/1.1/'})
        if dc_type is not None and dc_type.text == 'native-ad':
            return True
        return False


@grok.adapter(IRSSLink)
@grok.implementer(zeit.cms.content.interfaces.IUUID)
def no_uuid(context):
    return None


@grok.adapter(IRSSLink)
@grok.implementer(zeit.connector.interfaces.IWebDAVProperties)
def no_dav_props(context):
    return {}
