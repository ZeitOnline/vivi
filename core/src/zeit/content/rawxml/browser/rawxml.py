# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface
import zope.component

import zeit.cms.browser.listing
import zeit.cms.browser.interfaces

import zeit.content.rawxml.interfaces


class ListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    zope.component.adapts(zeit.content.rawxml.interfaces.IRawXML,
                          zeit.cms.browser.interfaces.ICMSLayer)
    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)

    author = ressort = page = volume = year = None
    type = 'rawxml'

    @property
    def title(self):
        return self.context.title

    searchableText = title
