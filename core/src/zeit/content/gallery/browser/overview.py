import zope.browser.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.i18n

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.content.gallery.interfaces
import zeit.wysiwyg.interfaces


class Overview(zeit.cms.browser.view.Base):
    title = _('Overview')

    def update(self):
        if 'form.actions.save_sorting' in self.request:
            self.context.updateOrder(self.request.get('images'))

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(self.context)


class Entry(zeit.cms.browser.view.Base):
    def view_url(self):
        return self.url(self.context.image, '@@view.html')


class ToggleWidget(zope.formlib.widget.SimpleInputWidget):
    template = zope.browserpage.ViewPageTemplateFile('togglewidget.pt')

    def __init__(self, field, request, values, title):
        super().__init__(field, request)
        self.values = values
        self.title = title

    def _toFormValue(self, value):
        return next(k for k, v in self.values.items() if v == value)

    def _toFieldValue(self, input):
        return self.values[input]

    def new_value(self):
        value = self._getFormValue()
        return next(k for k in self.values.keys() if k != value)

    def __call__(self):
        return self.template()


def toggle_widget_factory(values, title):
    def build(field, request):
        return ToggleWidget(field, request, values, title)

    return build


class ToggleVisible(zeit.edit.browser.form.InlineForm):
    legend = ''

    @property
    def form_fields(self):
        form_fields = zope.formlib.form.FormFields(
            zeit.content.gallery.interfaces.IGalleryEntry
        ).select('layout')
        form_fields['layout'].custom_widget = toggle_widget_factory(
            {
                'hidden': 'hidden',
                'default': None,
            },
            _('Switch visible'),
        )
        return form_fields


class EditCaption(zeit.edit.browser.form.InlineForm):
    legend = ''

    form_fields = zope.formlib.form.FormFields(
        zeit.content.gallery.interfaces.IGalleryEntry
    ).select('caption')


class Synchronise(zeit.cms.browser.view.Base):
    def __call__(self, redirect=''):
        self.context.reload_image_folder()
        self.send_message(_('Image folder was synchronised.'))
        url = self.url('@@overview.html')
        if redirect.lower() != 'false':
            self.redirect(url)
        return url


class SynchroniseMenuItem(zeit.cms.browser.menu.ActionMenuItem):
    title = _('Synchronise with image folder')
    action = '@@synchronise-with-image-folder'
    icon = '/@@/zeit.cms/icons/reload.png'


class UploadMenuItem(zeit.cms.browser.menu.ActionMenuItem):
    title = _('Upload Images')
    action = '@@upload-images'
    icon = '/@@/zeit.content.gallery/upload-icon.png'
