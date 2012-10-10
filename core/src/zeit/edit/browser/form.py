# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.form
import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.edit.browser.view
import zope.app.pagetemplate
import zope.formlib.form


class Forms(object):
    """View that collects all inline forms."""


FormGroup = zope.viewlet.viewlet.SimpleViewletClass('layout.forms.pt')


class FoldableFormGroup(zope.viewlet.viewlet.SimpleViewletClass(
        'layout.foldable-forms.pt')):

    folded_workingcopy = False
    folded_repository = False

    @property
    def folded(self):
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(self.context):
            return self.folded_workingcopy
        else:
            return self.folded_repository


FormLoader = zope.viewlet.viewlet.SimpleViewletClass('layout.form-loader.pt')


class InlineForm(zeit.cms.browser.form.WidgetCSSMixin,
                 zeit.cms.browser.form.PlaceholderMixin,
                 zope.formlib.form.SubPageEditForm,
                 zeit.edit.browser.view.UndoableMixin,
                 zeit.cms.browser.view.Base):

    template = zope.app.pagetemplate.ViewPageTemplateFile('inlineform.pt')

    css_class = None
    actions_visible = False

    @property
    def actions_css_class(self):
        css_class = 'form-controls'
        if self.actions_visible:
            css_class += ' actions-visible'
        return css_class

    @zope.formlib.form.action(_('Apply'))
    def handle_edit_action(self, action, data):
        self.mark_transaction_undoable()
        return super(InlineForm, self).handle_edit_action.success(data)
