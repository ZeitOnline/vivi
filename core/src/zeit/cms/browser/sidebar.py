# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent.mapping
import zeit.cms.browser.interfaces
import zope.annotation.factory
import zope.app.preference.interfaces
import zope.component
import zope.interface
import zope.security.interfaces


class PanelState(persistent.mapping.PersistentMapping):

    zope.interface.implements(zeit.cms.browser.interfaces.IPanelState)
    zope.component.adapts(zope.security.interfaces.IPrincipal)

    def folded(self, panel):
        return self.get(panel, False)

    def foldPanel(self, panel):
        self[panel] = True

    def unfoldPanel(self, panel):
        self[panel] = False


panelStateFactory = zope.annotation.factory(PanelState)


class Panel(object):

    def __call__(self, toggle_folding=None):
        if toggle_folding is not None:
            self.toggle_folding(toggle_folding)

    def css_class(self, panel_id):
        if self.folded(panel_id):
            return 'panel folded'
        return 'panel unfolded'

    def folded(self, panel_id):
        return self.panel_state.folded(panel_id)

    def toggle_folding(self, panel_id):
        if self.folded(panel_id):
            self.panel_state.unfoldPanel(panel_id)
        else:
            self.panel_state.foldPanel(panel_id)

    @zope.cachedescriptors.property.Lazy
    def panel_state(self):
        return zeit.cms.browser.interfaces.IPanelState(self.request.principal)


class Sidebar(object):

    @property
    def css_class(self):
        if self.folded:
            return 'sidebar-folded'
        return 'sidebar-expanded'

    @property
    def folded(self):
        return self.preferences.sidebarFolded

    def set_folded(self, folded):
        # XXX this type conversion is a little ridiculous
        self.preferences.sidebarFolded = True if folded == 'true' else False
        return self.css_class

    @zope.cachedescriptors.property.Lazy
    def preferences(self):
        return zope.app.preference.interfaces.IUserPreferences(
            self.context).cms_preferences
