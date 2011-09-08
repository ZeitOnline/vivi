# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.browser.adapter
import zope.publisher.interfaces


class ListRepresentation(
    zeit.cms.repository.browser.adapter.CMSContentListRepresentation):

    zope.component.adapts(zeit.content.cp.interfaces.IFeed,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.context.title


class CheckoutMenuItem(zeit.cms.browser.menu.ActionMenuItem):

    sort = -1

    def render(self):
        # this menu item intentionally left blank:
        # checking out a Feed object is not a sensible operation
        return ''
