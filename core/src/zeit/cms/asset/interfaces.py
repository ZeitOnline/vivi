# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.sources
import zope.interface
import zope.schema


class BadgeSource(zeit.cms.content.sources.XMLSource):

    config_url = 'source-badges'
    attribute = 'name'


class IBadges(zope.interface.Interface):

    badges = zope.schema.FrozenSet(
        title=_('Badges'),
        value_type=zope.schema.Choice(
            source=BadgeSource()))
