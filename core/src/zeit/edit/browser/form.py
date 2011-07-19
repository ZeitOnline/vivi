# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.browser.view
import zope.app.pagetemplate
import zope.formlib.form


class Forms(object):
    """View that collects all inline forms."""


"""Base class for groups of inline forms."""
FormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.forms.pt')

FoldableFormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.foldable-forms.pt')

FormLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.form-loader.pt')


class InlineForm(zope.formlib.form.SubPageEditForm,
                 zeit.edit.browser.view.UndoableMixin):

    template = zope.app.pagetemplate.ViewPageTemplateFile('inlineform.pt')

    def __call__(self):
        self.mark_transaction_undoable()
        return super(InlineForm, self).__call__()

    @property
    def widget_data(self):
        result = []
        for widget in self.widgets:
            css_class = ['widget-outer']
            if widget.error():
                css_class.append('error')
            result.append(dict(
                css_class=' '.join(css_class),
                widget=widget,
            ))
        return result
