# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zc.form.field

import zeit.cms.content.contentsource
import zeit.content.image.interfaces
from zeit.cms.i18n import MessageFactory as _


class IPortraitbox(zope.interface.Interface):

    name = zope.schema.TextLine(
        title=_('First and last name'))

    text = zeit.cms.content.field.XMLTree(
        title=_('Text'))

    image = zope.schema.Choice(
        title=_('Image'),
        source=zeit.content.image.interfaces.imageSource,
        required=False)


class PortraitboxSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.portraitbox'

    def verify_interface(self, value):
        return IPortraitbox.providedBy(value)

portraitboxSource = PortraitboxSource()


class IPortraitboxReference(zope.interface.Interface):

    portraitbox = zope.schema.Choice(
        title=_('Portraitbox'),
        required=False,
        source=portraitboxSource)
