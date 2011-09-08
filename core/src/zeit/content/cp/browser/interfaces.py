# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.viewlet.interfaces


class IEditorContentViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Viewlets which compose an area."""


class IEditBarViewletManager(zope.viewlet.interfaces.IViewletManager):
    """Vielets which compose an edit bar."""
