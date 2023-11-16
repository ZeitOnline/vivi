from datetime import timedelta
import zeit.cms.workflow.interfaces
import grokcore.component as grok
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zope.component
import zope.interface


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.workflow.interfaces.IPublicationStatus)
class PublicationStatus:
    def __init__(self, context):
        self.context = context

    @property
    def published(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context, None)
        if info is None:
            return None
        if not info.published:
            return 'not-published'
        times = zope.dublincore.interfaces.IDCTimes(self.context)
        grace = zeit.cms.workflow.interfaces.PUBLISH_DURATION_GRACE
        if (
            not times.modified
            or not info.date_last_published
            or info.date_last_published + timedelta(seconds=grace) > times.modified
        ):
            return 'published'
        return 'published-with-changes'


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zope.lifecycleevent.IObjectCopiedEvent)
def reset_publishinfo_on_copy(context, event):
    info = zeit.cms.workflow.interfaces.IPublishInfo(context, None)
    if info is None:
        return
    # most fields of IPublishInfo are marked readonly, so they don't get a
    # security declaration for writing
    info = zope.security.proxy.getObject(info)
    live = zope.component.getUtility(zeit.cms.content.interfaces.ILivePropertyManager)
    for name, field in zope.schema.getFields(zeit.cms.workflow.interfaces.IPublishInfo).items():
        prop = getattr(type(info), name)
        if not isinstance(prop, zeit.cms.content.dav.DAVProperty):
            continue
        if not live.is_writeable_live(prop.name, prop.namespace):
            continue
        current = getattr(info, name)
        if current != field.default:
            setattr(info, name, field.default)
