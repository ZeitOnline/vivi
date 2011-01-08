# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.settings.interfaces
import zeit.cms.browser.view


class EntryPage(zeit.cms.browser.view.Base):

    def __call__(self):
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        return self.redirect(
            self.url(settings.get_working_directory('online/$year/$volume')))
