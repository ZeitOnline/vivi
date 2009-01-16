# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Dublincore implementation."""

import zope.component
import zope.dublincore.interfaces
import zope.interface

import zeit.cms.interfaces
import zeit.cms.content.dav


class DCTimes(object):

    zope.component.adapts(zeit.cms.repository.interfaces.IRepositoryContent)
    zope.interface.implements(zope.dublincore.interfaces.IDCTimes)

    def __init__(self, context):
        self.context = context

    created = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['created'],
        u'DAV:',
        'creationdate')
    modified = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['modified'],
        u'DAV:',
        'getlastmodified')


@zope.component.adapter(DCTimes)
@zope.interface.implementer(zeit.cms.interfaces.IWebDAVProperties)
def webdav_properties(context):
    return zeit.cms.interfaces.IWebDAVProperties(context.context, None)
