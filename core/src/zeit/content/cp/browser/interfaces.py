# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.viewlet.interfaces


class IAreaContentViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Viewlets which compose an area."""


class IBoxContentViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Viewlets which compose a box."""

