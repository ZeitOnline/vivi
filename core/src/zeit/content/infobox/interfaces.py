# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zc.form.field

import zeit.cms.content.contentsource
from zeit.cms.i18n import MessageFactory as _


class IInfobox(zope.interface.Interface):

    supertitle = zope.schema.TextLine(title=_('Supertitle'))

    contents = zope.schema.Tuple(
        title=_('Contents'),
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(
                title=_('Title')),
              zc.form.field.HTMLSnippet(title=_("Text")),
            )))



class InfoboxSource(zeit.cms.content.contentsource.CMSContentSource):

    name = 'zeit.content.infobox'

    def verify_interface(self, value):
        return IInfobox.providedBy(value)

infoboxSource = InfoboxSource()


class IInfoboxReference(zope.interface.Interface):

    infobox = zope.schema.Choice(
        title=_('Infobox'),
        required=False,
        source=infoboxSource)
