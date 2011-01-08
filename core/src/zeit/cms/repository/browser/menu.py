# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zeit.cms.browser.menu
from zeit.cms.i18n import MessageFactory as _


class Rename(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Rename menu item."""

    title = _('Rename')


class Delete(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Delete menu item."""

    title = _('Delete')
