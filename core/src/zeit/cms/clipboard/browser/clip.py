# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface
import zope.publisher.interfaces

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing

import zeit.cms.clipboard.interfaces


class ClipListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.clipboard.interfaces.IClip,
                          zope.publisher.interfaces.IPublicationRequest)

    author = subtitle = byline = ressort = volume = page = year = None
    uniqueId = None
    searchableText = u''

    @property
    def title(self):
        return self.context.title


class ClipDragPane(object):

    @property
    def unique_id(self):
        clipbaord = zeit.cms.clipboard.interfaces.IClipboard(
            self.request.principal)
        tree = zope.component.getMultiAdapter(
            (clipbaord, self.request),
            name='tree.html')
        return tree.getUniqueId(self.context)

