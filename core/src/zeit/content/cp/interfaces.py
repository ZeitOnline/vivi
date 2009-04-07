# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zope.container.interfaces
import zope.interface
from zeit.content.cp.i18n import MessageFactory as _


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent,
                  zope.container.interfaces.IReadContainer):
    """XXX docme"""

    def __getitem__(area_key):
        """Return IArea for given key.

        area_key references <foo area="area_key"

        NOTE: currently the only valid keys are

            - lead
            - informatives
            - mosaik

        """

class IReadArea(zeit.cms.content.interfaces.IXMLRepresentation,
                zope.container.interfaces.IContained,
                zope.container.interfaces.IReadContainer):
    """Area on the CP which can be edited.

    This references a <region> or <cluster>

    """

class IWriteArea(zope.container.interfaces.IOrdered):
    """Modify area."""

    def add(item):
        """Add item to container."""

    def __delitem__(key):
        """Remove item."""


class IArea(IReadArea, IWriteArea):
    """Combined read/write interface to areas."""


class IRegion(IArea):
    """A region contains boxes."""


class ILeadRegion(IRegion):
    """The lead region."""


class ICluster(IArea):
    """A cluster contains regions."""


class IBox(zope.interface.Interface):
    """XXX A module which can be instantiated and added to the page."""

    type = zope.interface.Attribute("Type identifier.")


class IBoxFactory(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_('Box type'))

    def __call__():
        """Create box."""


class IPlaceHolder(IBox):
    """Placeholder."""


class ITeaserList(IBox):
    """A list of teasers."""


class ITeaserBar(IBox, IRegion):
    """A teaser bar is a bar in the teaser mosaic.

    The TeaserBar has a dual nature of being both a box and a region.

    """
