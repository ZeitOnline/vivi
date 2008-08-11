# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Implementation of the link content type."""

import zope.component
import zope.interface

import zeit.cms.content.adapter
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.syndication.interfaces

import zeit.content.link.interfaces


class Link(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing links to non-local content."""

    zope.interface.implements(zeit.content.link.interfaces.ILink)

    default_template = (
        '<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        '<head/><body/></link>')

    url = zeit.cms.content.property.ObjectPathProperty('.body.url')



linkFactory = zeit.cms.content.adapter.xmlContentFactory(Link)

resourceFactory = zeit.cms.content.adapter.xmlContentToResourceAdapterFactory(
    'link')
resourceFactory = zope.component.adapter(
    zeit.content.link.interfaces.ILink)(resourceFactory)


class FeedMetadataUpdater(object):
    """Add the expire/publication time to feed entry."""

    zope.component.adapts(zeit.content.link.interfaces.ILink)
    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    def __init__(self, context):
        self.context = context

    def update(self, entry):
        url = self.context.url
        if not url:
            url = ''
        entry.set('{http://namespaces.zeit.de/CMS/link}href', url)
