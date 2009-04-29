# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.contentsource
import zeit.cms.content.interfaces
import zeit.cms.syndication.interfaces
import zeit.content.cp.layout
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
    """A region contains blocks."""


class ILeadRegion(IRegion):
    """The lead region."""


class ICluster(IArea):
    """A cluster contains regions."""


class IBlock(zope.interface.Interface):
    """XXX A module which can be instantiated and added to the page."""

    type = zope.interface.Attribute("Type identifier.")


class ICMSContentIterable(zope.interface.Interface):
    """An iterable object iterating over CMSContent."""

    def __iter__():
        pass


class IBlockFactory(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_('Block type'))

    def __call__():
        """Create block."""


class IPlaceHolder(IBlock):
    """Placeholder."""


#
# Teaser block (aka teaser list)
#


class IReadTeaserList(IBlock, zeit.cms.syndication.interfaces.IReadFeed):

    referenced_cp = zope.schema.Choice(
        title=_("Fetch teasers from"),
        source=zeit.cms.content.contentsource.CMSContentSource(),
        required=False)
    autopilot = zope.schema.Bool(
        title=_("On Autopilot")
        )
    layout = zope.schema.Choice(
        title=_("Layout"),
        source=zeit.content.cp.layout.LayoutSource())

    @zope.interface.invariant
    def autopilot_requires_referenced_cp(self):
        if self.autopilot and not self.referenced_cp:
            raise zope.schema.ValidationError(
                _("Cannot activate autopilot without referenced centerpage"))
        return True



class IWriteTeaserList(zeit.cms.syndication.interfaces.IWriteFeed):
    pass


class ITeaserList(IReadTeaserList, IWriteTeaserList):
    """A list of teasers."""


class ITeaserBlockLayout(zope.interface.Interface):
    """Layout of a teaser block."""

    id = zope.schema.ASCIILine(title=u'Id used in xml to identify layout')
    title = zope.schema.TextLine(title=u'Human readable title.')

    image_pattern = zope.schema.ASCIILine(
        title=u'A match for the image to use in this layout');


class ITeaser(zeit.cms.content.interfaces.ICommonMetadata,
              zeit.cms.content.interfaces.IXMLContent):
    """A standalone teaser object which references the article."""


class ILeadTeasers(zope.interface.Interface):
    """A list containing the UID of the first teaser of each block in the lead
    area."""


class ITeaserBar(IBlock, IRegion):
    """A teaser bar is a bar in the teaser mosaic.

    The TeaserBar has a dual nature of being both a block and a region.

    """

