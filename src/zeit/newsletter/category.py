# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import WRITEABLE_LIVE
from zeit.cms.i18n import MessageFactory as _
import datetime
import grokcore.component as grok
import pytz
import zeit.cms.content.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.type
import zeit.connector.interfaces
import zeit.connector.search
import zeit.newsletter.interfaces
import zeit.newsletter.newsletter
import zope.component
import zope.interface


FIRST_RELEASED = zeit.connector.search.SearchVar(
    'date_first_released', 'http://namespaces.zeit.de/CMS/document')


DAILY_NAME = 'taeglich'


class NewsletterCategory(zeit.cms.repository.folder.Folder):

    zope.interface.implements(zeit.newsletter.interfaces.INewsletterCategory)

    zeit.cms.content.dav.mapProperties(
        zeit.newsletter.interfaces.INewsletterCategory,
        zeit.newsletter.interfaces.DAV_NAMESPACE,
        ['last_created'], writeable=WRITEABLE_LIVE)

    def create(self):
        now = datetime.datetime.now(pytz.UTC)
        newsletter = zeit.newsletter.newsletter.Newsletter()
        self.populate(newsletter)
        newsletter = self._add_newsletter(newsletter, now)
        self.last_created = now
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
        build = zope.component.queryAdapter(newsletter,
            zeit.newsletter.interfaces.IBuild, name=self.__name__)
        # XXX rethink strategy when no builder exists
        if build is not None:
            build(relevant_content)

    def _get_content_newer_than(self, timestamp):
        if timestamp is None:
            return
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        result = connector.search(
            [FIRST_RELEASED], (FIRST_RELEASED > timestamp.isoformat()))
        for unique_id, released in result:
            obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
            if obj is not None:
                yield obj


class NewsletterCategoryType(zeit.cms.repository.folder.FolderType):

    factory = NewsletterCategory
    interface = zeit.newsletter.interfaces.INewsletterCategory
    type = 'newsletter-category'
    title = _('Newsletter category')
    addform = zeit.cms.type.SKIP_ADD


class Builder(grok.Adapter):

    grok.context(zeit.newsletter.interfaces.INewsletter)
    grok.implements(zeit.newsletter.interfaces.IBuild)
    grok.baseclass()

    def __init__(self, context):
        # XXX adapt (category, newsletter) so we can get configuration from the
        # category?
        self.context = context
        # XXX introduce 'body' property on Newsletter?
        self.body = context[zeit.newsletter.newsletter.BODY_NAME]

    def create_group(self, title):
        group = zope.component.getAdapter(
            self.body, zeit.edit.interfaces.IElementFactory, name='group')()
        group.title = title
        return group

    def create_teaser(self, group, content):
        teaser = zope.component.getAdapter(
            group, zeit.edit.interfaces.IElementFactory, name='teaser')()
        teaser.reference = content
        return teaser


class DailyNewsletterBuilder(Builder):

    grok.name(DAILY_NAME)

    # XXX make configurable
    ressorts = (u'Politik', u'Wirtschaft', u'Meinung', u'Gesellschaft',
                u'Kultur', u'Wissen', u'Digital', u'Studium', u'Karriere',
                u'Lebensart', u'Reisen', u'Auto', u'Sport')

    def __call__(self, content_list):
        groups = self._group_by_ressort(content_list)
        for ressort in self.ressorts:
            entries = groups.get(ressort)
            if entries:
                group = self.create_group(ressort)
                for content in entries:
                    self.create_teaser(group, content)

    def _group_by_ressort(self, content_list):
        groups = {}
        for content in content_list:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                content, None)
            if metadata is None or metadata.ressort not in self.ressorts:
                continue
            groups.setdefault(metadata.ressort, []).append(content)
        return groups


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
