# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.publisher.interfaces.browser

import zeit.cms.repository.interfaces
import zeit.cms.browser.listing
import zeit.cms.browser.interfaces

import zeit.content.portraitbox.interfaces


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
    zeit.cms.interfaces.ICMSContent,
    zeit.content.portraitbox.interfaces.PortraitboxSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def content_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


@zope.component.adapter(
    zeit.content.portraitbox.interfaces.IPortraitboxReference,
    zeit.content.portraitbox.interfaces.PortraitboxSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def reference_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder,
    zeit.content.portraitbox.interfaces.PortraitboxSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def folder_browse_location(context, source):
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    personen = repository.get('personen')
    if personen is not None:
        return personen
    return context
