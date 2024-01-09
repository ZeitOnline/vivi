import zeit.cms.browser.view
import zeit.cms.settings.interfaces


class EntryPage(zeit.cms.browser.view.Base):
    def __call__(self):
        settings = zeit.cms.settings.interfaces.IGlobalSettings(self.context)
        return self.redirect(self.url(settings.get_working_directory('online/$year/$volume')))
