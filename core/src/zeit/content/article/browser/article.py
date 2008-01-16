# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component
import zope.interface
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
