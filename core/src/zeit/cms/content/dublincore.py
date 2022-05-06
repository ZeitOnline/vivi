import grokcore.component as grok
import pendulum
import zeit.cms.content.dav
import zeit.cms.repository.interfaces
import zeit.cms.workingcopy.interfaces
import zope.dublincore.interfaces


@grok.implementer(zope.dublincore.interfaces.IDCTimes)
class RepositoryDCTimes(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.context(zeit.cms.repository.interfaces.IRepositoryContent)

    created = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['created'],
        'DAV:',
        'creationdate')
    modified = zeit.cms.content.dav.DAVProperty(
        zope.dublincore.interfaces.IDCTimes['modified'],
        'DAV:',
        'getlastmodified')


class LocalDCTimes(RepositoryDCTimes):

    grok.context(zeit.cms.workingcopy.interfaces.ILocalContent)

    @property
    def modified(self):
        ts = self.context._p_mtime
        if ts is None:
            modified = super().modified
            if modified is None:
                annotations = zope.annotation.interfaces.IAnnotations(
                    self.context)
                modified = annotations.get(__name__)
        else:
            modified = pendulum.from_timestamp(ts)
        return modified

    @modified.setter
    def modified(self, value):
        # Store modified in annotations. Some code may set modified for
        # temporary objects or to have a modified date before database commit.
        annotations = zope.annotation.interfaces.IAnnotations(self.context)
        annotations[__name__] = value
