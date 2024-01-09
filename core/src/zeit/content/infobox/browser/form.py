import copy

import gocept.form.grouped
import zc.form.browser.combinationwidget
import zope.app.form.browser
import zope.cachedescriptors.property
import zope.formlib.form

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.interfaces
import zeit.content.infobox.infobox
import zeit.content.infobox.interfaces
import zeit.wysiwyg.browser.widget


class FormBase:
    form_fields = zope.formlib.form.FormFields(zeit.content.infobox.interfaces.IInfobox).select(
        'supertitle', 'contents', '__name__', 'ressort', 'sub_ressort'
    )

    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            (
                'supertitle',
                'contents',
            ),
            css_class='column-left wide-widgets',
        ),
        gocept.form.grouped.RemainingFields(_('Head'), css_class='column-right'),
    )

    for_display = False

    def __init__(self, context, request):
        super().__init__(context, request)

        if not self.for_display:
            contents = copy.copy(self.form_fields['contents'])
            contents.custom_widget = lambda context, request: (
                zope.app.form.browser.TupleSequenceWidget(
                    context,
                    zeit.content.infobox.interfaces.IInfobox['contents'],
                    request,
                    subwidget=ContentWidget,
                )
            )
            self.form_fields = self.form_fields.omit('contents') + (
                zope.formlib.form.FormFields(contents)
            )


class ContentWidget(zc.form.browser.combinationwidget.CombinationWidget):
    @zope.cachedescriptors.property.Lazy
    def widgets(self):
        field = self.context
        res = []
        assert len(field.fields) == 2
        for nr, f in enumerate(field.fields):
            f = f.bind(self.context)
            if nr == 0:  # Text
                w = zope.component.getMultiAdapter(
                    (
                        f,
                        self.request,
                    ),
                    self.widget_interface,
                )
            else:
                w = zeit.wysiwyg.browser.widget.FckEditorWidget(f, self.request)
            w.setPrefix(self.name + '.')
            res.append(w)
        return res


class Add(FormBase, zeit.cms.browser.form.AddForm):
    factory = zeit.content.infobox.infobox.Infobox
    title = _('Add infobox')


class Edit(FormBase, zeit.cms.browser.form.EditForm):
    title = _('Edit infobox')
    field_groups = (
        gocept.form.grouped.Fields(
            _('Texts'),
            (
                'supertitle',
                'contents',
            ),
            css_class='full-width wide-widgets',
        ),
    )


class Display(FormBase, zeit.cms.browser.form.DisplayForm):
    title = _('View infobox')
    for_display = True
