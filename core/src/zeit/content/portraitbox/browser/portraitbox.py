# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.publisher.interfaces.browser

import zeit.cms.browser.listing
import zeit.cms.browser.interfaces

import zeit.content.portraitbox.interfaces
import zeit.content.portraitbox.reference


class ListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(
        zeit.content.portraitbox.interfaces.IPortraitbox,
        zope.publisher.interfaces.browser.IBrowserRequest)

    author = ressort = page = volume = year = u''

    @property
    def title(self):
        return self.context.name

    searchableText = title


@zope.component.adapter(
    zeit.content.portraitbox.reference.PortraitboxReference,
    zeit.content.portraitbox.interfaces.PortraitboxSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def portraitboxreference_browse_location(context, source):
    # /personen!
    return zope.component.queryMultiAdapter(
        (context.context, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
