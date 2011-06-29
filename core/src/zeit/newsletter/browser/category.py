# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view


class AddAndCheckout(zeit.cms.browser.view.Base):

    def __call__(self):
        newsletter = self.context.create()
        self.redirect(self.url(newsletter, '@@checkout'))
