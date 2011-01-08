# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.menu
from zeit.cms.i18n import MessageFactory as _


class Global(zeit.cms.browser.menu.GlobalMenuItem):
    """Global settings menu item."""

    title = _("Global settings")
    viewURL = '@@global-settings.html'
    pathitem = '@@global-settings.html'
