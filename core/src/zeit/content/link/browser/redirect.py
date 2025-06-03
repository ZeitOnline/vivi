from urllib.parse import urlparse

import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
from zeit.cms.repository.copypastemove import previous_uniqueid
import zeit.cms.browser.menu
import zeit.cms.config
import zeit.content.link.redirect


class ISchema(zope.interface.Interface):
    target = zope.schema.TextLine(
        title=_('Redirect path'), constraint=zeit.cms.repository.browser.move.valid_name
    )


class Redirect(zeit.cms.browser.lightbox.Form):
    form_fields = zope.formlib.form.FormFields(ISchema)

    template = zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile('redirect.pt')

    def get_data(self):
        target = previous_uniqueid(self.context) or self.context.uniqueId
        return {'target': urlparse(target).path}

    @zope.formlib.form.action(_('Create redirect'))
    def link(self, action, data):
        target = zeit.cms.interfaces.ID_NAMESPACE + data['target'][1:]
        link = zeit.content.link.redirect.create(self.context, target)
        self.context = link  # also sets nextURL


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    title = _('Create redirect')
