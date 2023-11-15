from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.content.cp.cache


class Prewarm(zeit.cms.browser.view.Base):
    def __call__(self):
        zeit.content.cp.cache.prewarm_cache.delay(self.context.uniqueId)
        self.send_message(_('Prewarming, this might take some time'))
        self.redirect(self.url(self.context, '@@view.html'))
        return ''


class MenuItem(zeit.cms.browser.menu.ActionMenuItem):
    title = _('Prewarm cache')


class PrewarmManual(zeit.cms.browser.view.Base):
    def __call__(self):
        zeit.content.cp.cache.prewarm_cache.delay(self.request.form['uniqueId'])
        self.send_message(_('Prewarming, this might take some time'))
        self.redirect(self.url(self.context))
        return ''
