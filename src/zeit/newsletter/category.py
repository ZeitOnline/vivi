# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import datetime
import zeit.cms.content.dav
import zeit.cms.repository.folder
import zeit.cms.type
import zeit.newsletter.interfaces
import zeit.newsletter.newsletter
import zope.component
import zope.interface


class NewsletterCategory(zeit.cms.repository.folder.Folder):

    zope.interface.implements(zeit.newsletter.interfaces.INewsletterCategory)

    zeit.cms.content.dav.mapProperties(
        zeit.newsletter.interfaces.INewsletterCategory,
        zeit.newsletter.interfaces.DAV_NAMESPACE,
        ['last_created'], live=True)

    def create(self):
        now = datetime.datetime.now()
        newsletter = self._create_newsletter(now)
        self.populate(newsletter)
        self.last_created = now
        return newsletter

    def _create_newsletter(self, timestamp):
        folder = self._find_or_create_folder(timestamp)
        name = self._choose_name(folder, timestamp)
        folder[name] = zeit.newsletter.newsletter.Newsletter()
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

    def _get_content_newer_than(self, timestamp):
        return []


class NewsletterCategoryType(zeit.cms.repository.folder.FolderType):

    factory = NewsletterCategory
    interface = zeit.newsletter.interfaces.INewsletterCategory
    type = 'newsletter-category'
    title = _('Newsletter category')
    addform = zeit.cms.type.SKIP_ADD
