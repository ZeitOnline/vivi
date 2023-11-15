from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu
import zeit.cms.checkout.helper
import zeit.content.image.interfaces
import zope.app.pagetemplate
import zope.formlib.form


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    title = _('Bulk change image copyright')


class Form(zeit.cms.browser.lightbox.Form):
    form_fields = zope.formlib.form.FormFields(zeit.content.image.interfaces.IImageMetadata).select(
        'copyright'
    )

    template = zope.app.pagetemplate.ViewPageTemplateFile('copyright.pt')

    def get_data(self):
        # We don't have any initial data.
        return {}

    @zope.formlib.form.action(_('Set copyright'))
    def action_set_copyright(self, action, data):
        changed = []
        for name in self.context:
            obj = self.context[name]
            metadata = zeit.content.image.interfaces.IImageMetadata(obj, None)
            if metadata is None:
                continue
            zeit.cms.checkout.helper.with_checked_out(
                obj, lambda x: self.set_copyright(x, data['copyright'])
            )
            changed.append(name)

        self.send_message(
            _('Copyright changed for: ${changes}', mapping={'changes': ', '.join(changed)})
        )

    @staticmethod
    def set_copyright(obj, copyright):
        metadata = zeit.content.image.interfaces.IImageMetadata(obj)
        metadata.copyright = copyright
        return obj
