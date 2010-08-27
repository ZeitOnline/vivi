# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Adapters to integrate brightcove content with the rest of the CMS."""

import datetime
import grokcore.component
import grokcore.component
import lxml.objectify
import pytz
import zeit.brightcove.content
import zeit.brightcove.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.cms.workflow.interfaces
import zeit.workflow.interfaces
import zope.component
import zope.dublincore.interfaces
import zope.security.proxy

class BrightcoveContentPublicationStatus(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IBrightcoveContent)
    grokcore.component.implements(
        zeit.cms.workflow.interfaces.IPublicationStatus)

    @property
    def published(self):
        if self.context.item_state == "ACTIVE":
            return "published"
        return "not-published"



@grokcore.component.adapter(basestring,
                            name='http://video.zeit.de/')
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_cms_content(uniqueId):
    assert uniqueId.startswith('http://video.zeit.de/')
    name = uniqueId.replace('http://video.zeit.de/', '', 1)
    name = name.replace('/', ':', 1)
    repository = zope.component.getUtility(
        zeit.brightcove.interfaces.IRepository)
    try:
        return repository[name]
    except KeyError:
        return None


class UUID(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IBrightcoveContent)
    grokcore.component.implements(zeit.cms.content.interfaces.IUUID)

    @property
    def id(self):
        return self.context.uniqueId


class TimeBasedPublishing(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IVideo)
    grokcore.component.implements(
        zeit.workflow.interfaces.ITimeBasedPublishing)

    published = True

    @property
    def date_first_released(self):
        return self.context.date_first_released

    date_last_published = date_first_released

    def can_publish(self):
        # Videos/playlists are actually always published, or at least not
        # publishable in the CMS.
        return False

    released_from = date_first_released

    @property
    def released_to(self):
        return self.context.expires

    @property
    def release_period(self):
        return self.released_from, self.released_to


class Modified(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IVideo)
    grokcore.component.implements(zeit.cms.workflow.interfaces.IModified)

    @property
    def date_last_modified(self):
        return self.context.date_last_modified


class IDCPublishing(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IVideo)
    grokcore.component.implements(zope.dublincore.interfaces.IDCPublishing)

    @property
    def effective(self):
        return None

    @property
    def expires(self):
        return self.context.expires


class IDCTimes(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IVideo)
    grokcore.component.implements(zope.dublincore.interfaces.IDCTimes)

    @property
    def created(self):
        return self.context.date_created

    @property
    def modified(self):
        return self.context.date_last_modified

    @modified.setter
    def modified(self, value):
        self.context.date_last_modified = value


@grokcore.component.subscribe(
    zeit.brightcove.interfaces.IVideo,
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def set_last_modified(context, event):
    times = zope.dublincore.interfaces.IDCTimes(
        zope.security.proxy.removeSecurityProxy(context))
    times.modified = datetime.datetime.now(pytz.utc)


class CommonMetadata(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IBrightcoveContent)
    grokcore.component.implements(zeit.cms.content.interfaces.ICommonMetadata)

    @property
    def year(self):
        try:
            modified = int(self.context.data.get('lastModifiedDate'))
        except (TypeError, ValueError):
            return None
        return datetime.datetime.fromtimestamp(modified/1000).year

    @property
    def teaserTitle(self):
        return self.title

    @property
    def uniqueId(self):
        return self.context.uniqueId

    def __getattr__(self, key):
        if key in zeit.cms.content.interfaces.ICommonMetadata:
            return getattr(self.context, key, None)
        raise AttributeError(key)


class SemanticChange(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IBrightcoveContent)
    grokcore.component.implements(zeit.cms.content.interfaces.ISemanticChange)

    @property
    def last_semantic_change(self):
        return self.context.date_last_modified


class CommonMetadataVideo(CommonMetadata):

    grokcore.component.context(zeit.brightcove.interfaces.IVideo)

    @property
    def commentsAllowed(self):
        return self.context.allow_comments


@grokcore.component.adapter(
    zeit.brightcove.interfaces.IPlaylist, name='videos')
@grokcore.component.implementer(
    zeit.cms.relation.interfaces.IReferenceProvider)
def list_video_ids(context):
    if context.video_ids is None:
        return None
    l = []
    for name in context.video_ids:
        content = zeit.brightcove.content.BCContent()
        content.uniqueId = name
        l.append(content)
    return l


@grokcore.component.adapter(
    zeit.brightcove.interfaces.IBrightcoveContent,
    zeit.cms.browser.interfaces.ICMSSkin)
@grokcore.component.implementer(
    zeit.cms.browser.interfaces.IListRepresentation)
def list_repr(context, request):
    metadata = zeit.cms.content.interfaces.ICommonMetadata(context)
    return zope.component.queryMultiAdapter(
        (metadata, request),
        zeit.cms.browser.interfaces.IListRepresentation)


class VideoXMLReferenceUpdater(grokcore.component.Adapter):

    grokcore.component.context(zeit.brightcove.interfaces.IVideo)
    grokcore.component.name('brightcove-image')
    grokcore.component.implements(
        zeit.cms.content.interfaces.IXMLReferenceUpdater)

    def update(self, node):
        image_node = node.find('image')
        if image_node is not None:
            node.remove(image_node)
        if self.context.video_still:
            node.append(lxml.objectify.E.image(
                src=self.context.video_still))
        node.set('type', 'video')
