# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.publisher.interfaces.browser

import zeit.cms.browser.listing
import zeit.cms.browser.interfaces

import zeit.content.infobox.interfaces


class ListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(
        zeit.content.infobox.interfaces.IInfobox,
        zope.publisher.interfaces.browser.IBrowserRequest)

    author = ressort = page = volume = year = u''

    @property
    def title(self):
        return self.context.supertitle

    searchableText = title
