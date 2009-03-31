# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

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

class IArea(zeit.cms.content.interfaces.IXMLRepresentation,
            zope.container.interfaces.IContained,
            zope.container.interfaces.IReadContainer):
    """Area on the CP which can be edited.

    This references a <region> or <cluster>

    """


    # XXX needs to go on a "write" interface
    def add(item):
        """Add item to container.

        XXX

        """



    # __iter__ ? __setitem__? Looks like we actually want an IOrderedContainer.


class IRegion(IArea):
    """A region contains boxes."""


class ICluster(IArea):
    """A cluster contains regions."""


class IBox(zope.interface.Interface):
    """XXX A module which can be instanciated an added to the page."""


class IBoxFactory(zope.interface.Interface):

    title = zope.schema.TextLine(
        title=_('Box type'))

    def __call__():
        """Create box."""


class IPlaceHolder(IBox):
    """Placeholder."""


class ITeaserList(IBox):

    title = zope.schema.Text(
        title=_('Test attribute'))
