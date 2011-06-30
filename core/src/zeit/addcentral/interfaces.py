# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zope.interface
import zope.schema


class IContentAdder(zope.interface.Interface):

    type_ = zope.schema.Choice(
        title=_("Type"),
        source=zeit.cms.content.sources.AddableCMSContentTypeSource())

    ressort = zope.schema.Choice(
        title=_("Ressort"),
        source=zeit.cms.content.sources.NavigationSource(),
        required=False)

    sub_ressort = zope.schema.Choice(
        title=_('Sub ressort'),
        source=zeit.cms.content.sources.SubNavigationSource(),
        required=False)

    year = zope.schema.Int(
        title=_("Year"),
        min=1900,
        max=2100)

    month = zope.schema.Int(
        title=_("Month"),
        min=1,
        max=12)
