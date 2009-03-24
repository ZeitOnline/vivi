# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zope.interface
from zeit.content.cp.i18n import MessageFactory as _


class ICenterPage(zeit.cms.content.interfaces.ICommonMetadata,
                  zeit.cms.content.interfaces.IXMLContent):
    """XXX docme"""

    def __getitem__(area_key):
        """Return IEditableArea for given key.

        area_key references <foo area="area_key"

        NOTE: currently the only valid keys are

            - lead
            - informatives
            - teaser-mosaik

        """

class IEditableArea(zeit.cms.content.interfaces.IXMLRepresentation):
    """Area on the CP which can be edited.

    This references a <region> or <cluster>

    """

    def __getitem__(xxx):
        """XXX"""

    # __iter__ ? __setitem__? Looks like we actually want an IOrderedContainer.


class IModule(zope.interface.Interface):
    """A module which can be instanciated an added to the page."""


class IWeather(IModule):

    city= zope.schema.TextLine(title=_('City'))


class IModuleFactory(zope.interface.Interface):

    def __call__(node):
        """XXX"""
