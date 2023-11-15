import zeit.cms.browser.view


class Checkin(zeit.cms.browser.view.Base):
    def __call__(self):
        return self.redirect(self.url(self.context.references, '@@view.html'))
