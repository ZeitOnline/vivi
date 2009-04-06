# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.syndication.feed
import zeit.cms.syndication.interfaces
import zeit.content.cp.box
import zeit.content.cp.interfaces
import zope.container.interfaces
import zope.interface
from zeit.content.cp.i18n import MessageFactory as _


class TeaserList(zeit.content.cp.box.Box,
                 zeit.cms.syndication.feed.Feed):

    zope.interface.implementsOnly(
        zeit.content.cp.interfaces.ITeaserList,
        zeit.cms.syndication.interfaces.IFeed,
        zope.container.interfaces.IContained)

    #title = zeit.cms.content.property.ObjectPathProperty('.title')
    object_limit = None

    @property
    def entries(self):
        return self.xml


TeaserListFactory = zeit.content.cp.box.boxFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    TeaserList, 'teaser', _('List of teasers'))
