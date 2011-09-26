# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.related.interfaces
import zope.interface
import zope.schema


DAV_NAMESPACE = 'http://namespaces.zeit.de/CMS/brightcove'


class IAPIConnection(zope.interface.Interface):
    """Brightcove API connection."""


class IBrightcoveObject(zope.interface.Interface):
    """A representation of an object as stored in Brightcove."""


class SerieSource(zeit.cms.content.sources.SimpleXMLSource):
    config_url = 'source-serie'
    product_configuration = 'zeit.brightcove'


class IRepository(zope.interface.Interface):
    """legacy interface."""
