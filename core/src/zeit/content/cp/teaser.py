# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.box
import zeit.content.cp.interfaces
import zope.interface
from zeit.content.cp.i18n import MessageFactory as _


class TeaserList(zeit.content.cp.box.Box):

    zope.interface.implements(zeit.content.cp.interfaces.ITeaserList)

    title = zeit.cms.content.property.ObjectPathProperty('.title')


TeaserListFactory = zeit.content.cp.box.boxFactoryFactory(
    TeaserList, 'teaser', _('List of teasers'))
