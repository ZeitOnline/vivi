# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
"""Implementation of the link content type."""

import zeit.cms.type
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.metadata
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zeit.cms.interfaces
import zeit.content.link.interfaces
import zope.component
import zope.interface


class Link(zeit.cms.content.metadata.CommonMetadata):
    """A type for managing links to non-local content."""

    zope.interface.implements(zeit.content.link.interfaces.ILink,
                              zeit.cms.interfaces.IEditorialContent)

    default_template = (
        '<link xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        '<head/><body/></link>')

    url = zeit.cms.content.property.ObjectPathProperty('.body.url')
    target = zeit.cms.content.property.ObjectPathProperty('.body.target')



class LinkType(zeit.cms.type.XMLContentTypeDeclaration):

    factory =  Link
    interface = zeit.content.link.interfaces.ILink
    title = _('Link')
    type = 'link'


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add the expire/publication time to feed entry."""

    zope.component.adapts(zeit.content.link.interfaces.ILink)

    def update(self, entry):
        url = self.context.url
        if not url:
            url = ''
        entry.set('{http://namespaces.zeit.de/CMS/link}href', url)

        target_attribute = '{http://namespaces.zeit.de/CMS/link}target'
        if self.context.target:
            entry.set(target_attribute, self.context.target)
        else:
            entry.attrib.pop(target_attribute, None)

