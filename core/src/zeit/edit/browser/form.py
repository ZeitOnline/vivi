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

class DiverFormGroup(zope.viewlet.viewlet.SimpleViewletClass('layout.diver-forms.pt')):
    """ Contains all diver forms."""

    def forms(self):
        """Returns all actual views that belong to this form group."""
        # XXX the wohle code here is rather icky, but there doesn't seem to be
        # a cleaner way
        from zeit.content.article.interfaces import IArticle
        from zeit.cms.browser.interfaces import ICMSLayer
        from zeit.edit.interfaces import IContentViewletManager

        # resolve wrapper class that ZCML creates for views and viewlets to get
        # to the original class
        form_group_class = self.__class__.__bases__[0]

        result = []
        for reg in zope.component.getGlobalSiteManager().registeredAdapters():
            # step 1: get all viewlets which have ourselves as the view
            required = (
                IArticle,
                ICMSLayer,
                zope.interface.implementedBy(form_group_class),
                IContentViewletManager
                )
            if reg.required != required:
                continue

            # step 2: these viewlets are form-loaders that load an actual view
            # of the same name, so we resolve that to get to the actual form
            form = zope.component.getMultiAdapter(
                (self.context, self.request), name=reg.name)
            result.append(form)
        return result


class InlineForm(zope.formlib.form.SubPageEditForm,
                 zeit.edit.browser.view.UndoableMixin,
                 zeit.cms.browser.view.Base):

    template = zope.app.pagetemplate.ViewPageTemplateFile('inlineform.pt')

    css_class = None

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


class DiverForm(InlineForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile('diver.pt')

    css_class = 'diver-form'
