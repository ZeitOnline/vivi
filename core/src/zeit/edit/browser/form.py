# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.edit.browser.view
import zope.app.pagetemplate
import zope.formlib.form


class Forms(object):
    """View that collects all inline forms."""


FormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.forms.pt')

FoldableFormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.foldable-forms.pt')

FormLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.form-loader.pt')


class InlineForm(zeit.cms.browser.form.WidgetCSSMixin,
                 zope.formlib.form.SubPageEditForm,
                 zeit.edit.browser.view.UndoableMixin,
                 zeit.cms.browser.view.Base):

    template = zope.app.pagetemplate.ViewPageTemplateFile('inlineform.pt')

    css_class = None

    def __call__(self):
        self.mark_transaction_undoable()
        return super(InlineForm, self).__call__()
