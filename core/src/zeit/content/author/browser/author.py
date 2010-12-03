# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore
import zeit.cms.browser.listing
import zeit.content.image.interfaces
import zope.publisher.interfaces


class AuthorListRepresentation(
    grokcore.component.MultiAdapter,
    zeit.cms.browser.listing.BaseListRepresentation):

    grokcore.component.adapts(
        zeit.content.author.interfaces.IAuthor,
        zope.publisher.interfaces.IPublicationRequest)
    grokcore.component.implements(
        zeit.cms.browser.interfaces.IListRepresentation)

    ressort = page = volume = year = author = u''

    @property
    def title(self):
        return self.context.display_name

    @property
    def searchableText(self):
        return self.context.display_name
