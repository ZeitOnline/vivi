# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view


class Checkin(zeit.cms.browser.view.Base):

    def __call__(self):
        return self.redirect(self.url(self.context.references, '@@view.html'))
