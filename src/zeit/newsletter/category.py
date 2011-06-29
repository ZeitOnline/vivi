# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import datetime
import zeit.cms.repository.folder
import zeit.cms.type
import zeit.newsletter.interfaces
import zeit.newsletter.newsletter
import zope.interface


class NewsletterCategory(zeit.cms.repository.folder.Folder):

    zope.interface.implements(zeit.newsletter.interfaces.INewsletterCategory)

    def create(self):
        newsletter = self._create_newsletter(datetime.datetime.now())
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


class NewsletterCategoryType(zeit.cms.repository.folder.FolderType):

    factory = NewsletterCategory
    interface = zeit.newsletter.interfaces.INewsletterCategory
    type = 'newsletter-category'
    title = _('Newsletter category')
    addform = zeit.cms.type.SKIP_ADD
