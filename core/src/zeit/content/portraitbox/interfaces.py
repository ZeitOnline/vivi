# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zc.form.field

import zeit.cms.content.contentsource
from zeit.cms.i18n import MessageFactory as _


class IPortraitbox(zope.interface.Interface):

    supertitle = zope.schema.TextLine(title=_('Supertitle'))

    contents = zope.schema.Tuple(
        title=_('Contents'),
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(
                title=_('Title')),
             zope.schema.Text(
                 title=_('Text')),
            )))


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
