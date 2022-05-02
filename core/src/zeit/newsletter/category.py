from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.cms.i18n import MessageFactory as _
import datetime
import grokcore.component as grok
import persistent
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.connector.interfaces
import zeit.connector.search
import zeit.content.video.interfaces
import zeit.newsletter.interfaces
import zeit.newsletter.newsletter
import zope.component
import zope.container.contained
import zope.dublincore.interfaces
import zope.interface
import zope.security.proxy


FIRST_RELEASED = zeit.connector.search.SearchVar(
    'date_first_released', 'http://namespaces.zeit.de/CMS/document')

DAILY_NEWSLETTER = zeit.connector.search.SearchVar(
    'DailyNL', zeit.cms.interfaces.DOCUMENT_SCHEMA_NS)


DAILY_NAME = 'taeglich'


@zope.interface.implementer(zeit.newsletter.interfaces.INewsletterCategory)
class NewsletterCategoryBase:

    zeit.cms.content.dav.mapProperties(
        zeit.newsletter.interfaces.INewsletterCategory,
        zeit.newsletter.interfaces.DAV_NAMESPACE,
        ['last_created'], writeable=WRITEABLE_LIVE)

    zeit.cms.content.dav.mapProperties(
        zeit.newsletter.interfaces.INewsletterCategory,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ['mandant', 'recipientlist', 'recipientlist_test',
         'subject', 'ressorts', 'video_playlist',
         'ad_bottom_href', 'ad_bottom_title',
         'ad_bottom_text', 'ad_bottom_image',
         'ad_middle_groups_above', 'ad_middle_href', 'ad_middle_title',
         'ad_middle_text', 'ad_middle_image',
         'ad_thisweeks_groups_above', 'ad_thisweeks_href',
         'ad_thisweeks_title', 'ad_thisweeks_text', 'ad_thisweeks_image',
         ] + ['ad_thisweeks_on_%d' % dow for dow in range(7)])

    def __init__(self):
        if not self.ressorts:
            self.ressorts = ()
        for dow in range(7):
            setattr(self, 'ad_thisweeks_on_%d' % dow, True)


@zope.interface.implementer(
    zeit.newsletter.interfaces.IRepositoryCategory,
    zeit.cms.repository.interfaces.INonRecursiveCollection)
class NewsletterCategory(NewsletterCategoryBase,
                         zeit.cms.repository.folder.Folder):

    def create(self):
        now = datetime.datetime.now(pytz.UTC)
        newsletter = zeit.newsletter.newsletter.Newsletter()
        newsletter.subject = self.subject.format(
            today=now.strftime('%d.%m.%Y'))
        self.populate(newsletter)
        # XXX It would be a good idea to pass the exact same timestamp from
        # here down to the connector search that will be stored as the
        # last_created date later when the newsletter has been published. Even
        # before #VIV-510, this has not been the case, but now that we use the
        # newsletter object's created date which is in turn set when adding
        # the newsletter to the object graph, this has become trickier. Simply
        # adding the newsletter before populating it makes it come up empty.
        newsletter = self._add_newsletter(newsletter, now)
        return newsletter

    def _add_newsletter(self, newsletter, timestamp):
        folder = self._find_or_create_folder(timestamp)
        name = self._choose_name(folder, timestamp)
        folder[name] = newsletter
        return folder[name]

    def _find_or_create_folder(self, timestamp):
        name = timestamp.strftime('%Y-%m')
        if name not in self:
            self[name] = zeit.cms.repository.folder.Folder()
        return self[name]

    def _choose_name(self, folder, timestamp):
        count = 1
        while True:
            name = '%s-%s' % (timestamp.strftime('%d'), count)
            if name not in folder:
                return name
            count += 1

    def populate(self, newsletter):
        relevant_content = self._get_content_newer_than(self.last_created)
        build = zope.component.queryMultiAdapter(
            (self, newsletter), zeit.newsletter.interfaces.IBuild)
        # XXX rethink strategy when no builder exists
        if build is not None:
            build(relevant_content)

    def _get_content_newer_than(self, timestamp):
        if timestamp is None:
            return
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        now = datetime.datetime.now(pytz.UTC)
        result = connector.search([FIRST_RELEASED, DAILY_NEWSLETTER], (
            FIRST_RELEASED.between(timestamp.isoformat(), now.isoformat()) &
            (DAILY_NEWSLETTER == 'yes')))
        for item in result:
            unique_id = item[0]
            obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
            if obj is not None:
                yield obj


class NewsletterCategoryType(zeit.cms.repository.folder.FolderType):

    factory = NewsletterCategory
    interface = zeit.newsletter.interfaces.INewsletterCategory
    type = 'newsletter-category'
    title = _('Newsletter category')
    addform = zeit.cms.type.SKIP_ADD


@zope.interface.implementer(zeit.newsletter.interfaces.ILocalCategory)
class LocalCategory(NewsletterCategoryBase,
                    persistent.Persistent,
                    zope.container.contained.Contained):
    pass


@grok.adapter(zeit.newsletter.interfaces.INewsletterCategory)
@grok.implementer(zeit.newsletter.interfaces.ILocalCategory)
def local_category_factory(context):
    local = LocalCategory()
    local.uniqueId = context.uniqueId
    local.__name__ = context.__name__
    zeit.connector.interfaces.IWebDAVWriteProperties(local).update(
        zeit.connector.interfaces.IWebDAVReadProperties(
            zope.security.proxy.getObject(context)))
    return local


@grok.implementer(zeit.newsletter.interfaces.IBuild)
class Builder(grok.MultiAdapter):

    grok.adapts(zeit.newsletter.interfaces.INewsletterCategory,
                zeit.newsletter.interfaces.INewsletter)

    def __init__(self, category, newsletter):
        self.category = category
        self.context = newsletter

    def create_group(self, title):
        group = zope.component.getAdapter(
            self.context.body,
            zeit.edit.interfaces.IElementFactory, name='group')()
        group.title = title
        return group

    def create_teaser(self, group, content):
        teaser = zope.component.getAdapter(
            group, zeit.edit.interfaces.IElementFactory, name='teaser')()
        teaser.reference = content
        return teaser

    def __call__(self, content_list):
        groups = self._group_by_ressort(content_list, self.category.ressorts)
        groups_above = 0
        for ressort in self.category.ressorts:
            entries = groups.get(ressort)
            ressort_title = zeit.cms.content.interfaces.ICommonMetadata[
                'ressort'].source.factory.getTitle(self.category, ressort)
            group = self.create_group(ressort_title)
            for content in entries:
                self.create_teaser(group, content)
            groups_above += 1
            if groups_above == self.category.ad_middle_groups_above:
                self.create_advertisement('middle')
            if groups_above == self.category.ad_thisweeks_groups_above:
                weekday = datetime.date.today().weekday()
                if getattr(self.category, 'ad_thisweeks_on_%d' % weekday):
                    self.create_advertisement('thisweeks')
        self.create_video_group()
        self.create_advertisement('bottom')

    def _group_by_ressort(self, content_list, accept_ressorts):
        groups = {}
        for ressort in accept_ressorts:
            groups[ressort] = []
        for content in content_list:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            if metadata is None or metadata.ressort not in accept_ressorts:
                continue
            groups[metadata.ressort].append(content)
        return groups

    def create_video_group(self):
        if self.category is None:
            return
        group = self.create_group('Video')
        if self.category.last_created is None:
            return
        playlist = zeit.cms.interfaces.ICMSContent(
            self.category.video_playlist, None)
        if playlist is None:
            return
        if not zeit.content.video.interfaces.IPlaylist.providedBy(playlist):
            return
        for video in playlist.videos:
            created = zope.dublincore.interfaces.IDCTimes(video).created
            if created is None or created < self.category.last_created:
                continue
            self.create_teaser(group, video)

    def create_advertisement(self, position):
        zope.component.getAdapter(
            self.context.body,
            zeit.edit.interfaces.IElementFactory,
            name='advertisement-%s' % position)()


@grok.adapter(
    zeit.newsletter.interfaces.INewsletter,
    zeit.cms.content.interfaces.IContentAdder)
@grok.implementer(zeit.cms.content.interfaces.IAddLocation)
def daily_newsletter(type_, adder):
    # This is not ready for multiple newsletter categories, since there always
    # will be just one INewsletter interface. But since there only is one
    # category at the moment (the daily newsletter), it's okay for now.
    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    return repository['newsletter'][DAILY_NAME]
