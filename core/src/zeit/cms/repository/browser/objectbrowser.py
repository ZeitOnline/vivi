# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface

import zeit.cms.repository.interfaces
import zeit.cms.interfaces
import zeit.cms.browser.interfaces


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder,
    zeit.cms.interfaces.ICMSContentType)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def folder_default_browse_location(context, schema):
    return context


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.interfaces.ICMSContentType)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def content_default_browse_location(context, schema):
    return zope.component.queryMultiAdapter(
        (context.__parent__, schema),
        zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
