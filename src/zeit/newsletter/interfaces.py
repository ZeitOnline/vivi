# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zeit.edit.interfaces
import zope.container.interfaces
import zope.interface


class INewsletter(zeit.cms.content.interfaces.IXMLContent,
                  zope.container.interfaces.IReadContainer):
    pass


class IBody(zeit.edit.interfaces.IArea):
    pass


class IGroup(zeit.edit.interfaces.IArea,
             zeit.edit.interfaces.IBlock):
    pass


class ITeaser(zeit.edit.interfaces.IBlock):
    pass


class INewsletterCategory(zope.interface.Interface):
    pass
