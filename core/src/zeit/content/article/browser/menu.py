# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.menu

class WorkflowMenuItem(zeit.cms.browser.menu.ContextViewsMenu):
    """The Workflow menu item which is active when no other item is active."""
    def render(self):
        return ''
