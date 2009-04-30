# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zeit.content.cp.browser.teaserblock


class EditProperties(zeit.content.cp.browser.teaserblock.EditProperties):

    interface = zeit.content.cp.interfaces.ITeaserBar

    form_fields = []

    @property
    def form(self):
        return ''


class ChangeLayout(zeit.content.cp.browser.teaserblock.ChangeLayout):

    interface = zeit.content.cp.interfaces.ITeaserBar
