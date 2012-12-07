# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.sourcefactory.source
import zeit.cms.content.sources
import zope.interface
import zope.interface.interfaces
import zope.schema


# XXX kludge to be able to identify the source later on (to register widgets
# for it), we should create a better mechanism for this purpose.
class FactoredBadgeSource(
    zc.sourcefactory.source.FactoredContextualSource):
    pass


class BadgeSource(zeit.cms.content.sources.XMLSource):

    config_url = 'source-badges'
    attribute = 'name'
    source_class = FactoredBadgeSource


class IBadges(zope.interface.Interface):

    badges = zope.schema.FrozenSet(
        title=_('Badges'),
        value_type=zope.schema.Choice(
            source=BadgeSource()))


class IAssetInterface(zope.interface.interfaces.IInterface):
    """The interface for asset interfaces."""
