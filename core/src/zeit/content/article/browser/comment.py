# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Comment browser integration."""

import zope.component

import zope.app.appsetup.interfaces

import zeit.cms.browser.interfaces
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.content.article.comment
import zeit.content.article.interfaces


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def register_asset_interface(event):
    zeit.cms.content.browser.form.AssetBase.add_asset_interface(
        zeit.content.article.interfaces.IAggregatedComments)

@zope.component.adapter(
    zeit.content.article.comment.AggregatedComments,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def comment_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
