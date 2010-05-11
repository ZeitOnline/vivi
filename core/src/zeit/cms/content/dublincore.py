# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Dublincore implementation."""

import grokcore.component
import zeit.cms.content.dav
import zeit.cms.repository.interfaces
import zope.dublincore.interfaces


class RepositoryDCTimes(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.context(
        zeit.cms.repository.interfaces.IRepositoryContent)
    grokcore.component.implements(zope.dublincore.interfaces.IDCTimes)

    created = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['created'],
        u'DAV:',
        'creationdate')
    modified = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['modified'],
        u'DAV:',
        'getlastmodified')
