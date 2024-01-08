import zope.app.form.browser.interfaces
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
    layout_source = zeit.content.gallery.interfaces.IGalleryEntry['layout'].vocabulary

    def update(self):
        if 'form.actions.save_sorting' in self.request:
            self.context.updateOrder(self.request.get('images'))
        entries = []
        for entry in self.context.values():
            entries.append(
                {
                    '__name__': entry.__name__,
                    'caption': entry.caption,
                    'css_class': 'layout-%s' % (entry.layout if entry.layout else ''),
                    'image': entry.image,
                    'layout': self.get_entry_layout(entry),
                    'text': self.get_text(entry),
                    'thumbnail': entry.thumbnail,
                    'title': entry.title,
                    'url': self.url(entry),
                }
            )
        self.entries = entries

    def get_text(self, entry):
        return zeit.wysiwyg.interfaces.IHTMLConverter(entry).to_html(entry.text)

    def get_entry_layout(self, entry):
        try:
            title = self.layout_terms.getTerm(entry.layout).title
        except KeyError:
            return ''
        else:
            return zope.i18n.translate(title, context=self.request)

    @zope.cachedescriptors.property.Lazy
    def metadata(self):
        return zeit.cms.content.interfaces.ICommonMetadata(self.context)

    @zope.cachedescriptors.property.Lazy
    def layout_terms(self):
        return zope.component.getMultiAdapter(
            (self.layout_source, self.request), zope.app.form.browser.interfaces.ITerms
        )


class Synchronise(zeit.cms.browser.view.Base):
    def __call__(self, redirect=''):
        self.context.reload_image_folder()
        self.send_message(_('Image folder was synchronised.'))
        url = self.url('@@overview.html')
        if redirect.lower() != 'false':
            self.redirect(url)
        return url


class UploadImage(zeit.cms.browser.view.JSON):
    def json(self):
        view = zope.component.getMultiAdapter(
            (self.context.image_folder, self.request), name='zeit.content.image.Add'
        )
        view.checkout = False
        view()
        result = {}
        if view.errors:
            if len(view.errors) == 1 and view.errors[0].field_name == 'blob':
                # That was not an image.
                self.request.response.setStatus(415)
                result['error'] = 'NotAnImage'
            else:
                # Okay, something else.
                __traceback_info__ = (view.errors,)
                self.request.response.setStatus(500)
        else:
            self.request.response.setStatus(201)  # Created
        return result


class SynchroniseMenuItem(zeit.cms.browser.menu.ActionMenuItem):
    title = _('Synchronise with image folder')
    action = '@@synchronise-with-image-folder'
    icon = '/@@/zeit.cms/icons/reload.png'
