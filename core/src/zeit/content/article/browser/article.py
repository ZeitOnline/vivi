# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.publisher.interfaces

import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.content.article.interfaces


class ArticleListRepresentation(
    zeit.cms.browser.listing.CommonListRepresentation):
    """Adapter for listing article content resources"""

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.content.article.interfaces.IArticle,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def metadata(self):
        # XXX don't put out html here!
        url = zope.traversing.browser.absoluteURL(self, self.request)
        id = self.context.__name__
        return ('<span class="Metadata">%s/metadata_preview</span><span'
                ' class="DeleteId">%s</span>' %(url, id))
