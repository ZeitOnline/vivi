from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.listing
import zeit.content.dynamicfolder.interfaces
import zope.formlib.form


class FormBase:
    form_fields = zope.formlib.form.FormFields(zeit.content.dynamicfolder.interfaces.IDynamicFolder)


class DisplayForm(FormBase, zeit.cms.browser.form.DisplayForm):
    pass


class EditForm(FormBase, zeit.cms.browser.form.EditForm):
    title = _('Edit metadata')
    form_fields = FormBase.form_fields.omit('__name__')


class View(zeit.cms.browser.listing.Listing, zeit.cms.browser.view.Base):
    columns = (
        zeit.cms.browser.listing.GetterColumn(
            title=_('File name'),
            # zc.table can't deal with spaces in colum names
            name='filename',
            getter=lambda i, f: i.__name__,
        ),
        zeit.cms.browser.listing.MetadataColumn(
            'Metadaten', name='metadata', searchable_text=False
        ),
    )

    @property
    def content(self):
        result = []
        for name in sorted(self.context.keys()):
            result.append(ContentPlaceholder(name, self.context, self.url(self.context, name)))
        return result


class ContentPlaceholder:
    def __init__(self, name, parent, url):
        self.__name__ = name
        self.__parent__ = parent
        self.uniqueId = parent.uniqueId + name
        self.url = url
