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
        zodb = self.context._p_mtime
        if zodb is not None:
            return pendulum.from_timestamp(zodb)
        checkin = super().modified
        if checkin is not None:
            return checkin
        annotations = zope.annotation.interfaces.IAnnotations(self.context)
        return annotations.get(__name__)

    @modified.setter
    def modified(self, value):
        # Store modified in annotations. Some code may set modified for
        # temporary objects or to have a modified date before database commit.
        annotations = zope.annotation.interfaces.IAnnotations(self.context)
        annotations[__name__] = value
