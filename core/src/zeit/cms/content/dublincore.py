import grokcore.component as grok
import pendulum
import zope.dublincore.interfaces

import zeit.cms.content.dav
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces


@grok.implementer(zope.dublincore.interfaces.IDCTimes)
class RepositoryDCTimes(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.context(zeit.cms.repository.interfaces.IRepositoryContent)

    created = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['created'], 'DAV:', 'creationdate'
    )
    modified = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['modified'], 'DAV:', 'getlastmodified'
    )


class LocalDCTimes(RepositoryDCTimes):
    grok.context(zeit.cms.workingcopy.interfaces.ILocalContent)

    @property
    def modified(self):
        return self._zodb or super().modified

    @property
    def _zodb(self):
        if self.context._p_mtime is None:
            return None
        return pendulum.from_timestamp(self.context._p_mtime)

    @modified.setter
    def modified(self, value):
        # Some code may set modified for temporary objects or to have a
        # modified date before database commit.
        pass
