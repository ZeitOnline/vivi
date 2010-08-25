# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Dublincore implementation."""

import datetime
import grokcore.component
import pytz
import zeit.cms.content.dav
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
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


class LocalDCTimes(RepositoryDCTimes):

    grokcore.component.context(zeit.cms.workingcopy.interfaces.ILocalContent)

    @property
    def modified(self):
        ts = self.context._p_mtime
        if ts is None:
            modified = super(LocalDCTimes, self).modified
            if modified is None:
                annotations = zope.annotation.interfaces.IAnnotations(
                    self.context)
                modified = annotations.get(__name__)
        else:
            modified = datetime.datetime.fromtimestamp(ts, pytz.UTC)
        return modified

    @modified.setter
    def modified(self, value):
        # Store modified in annotations. Some code may set modified for temporary
        # objects or to have a modified date before database commit.
        annotations = zope.annotation.interfaces.IAnnotations(self.context)
        annotations[__name__] = value
