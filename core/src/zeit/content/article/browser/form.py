# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import datetime

import zope.formlib.form
import zope.publisher.interfaces.browser
import zope.session.interfaces

import zc.resourcelibrary
import gocept.form.grouped

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.cms.content.template
import zeit.cms.content.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.content.article.interfaces


class TemplateSource(zeit.cms.content.template.BasicTemplateSource):

    template_manager = 'Article templates'


class ITemplateChooserSchema(zope.interface.Interface):

    template = zope.schema.Choice(
        title=_("Template"),
        source=TemplateSource(),
        required=False)


class ChooseTemplate(gocept.form.grouped.Form):

    title = _("Choose template")
    form_fields = zope.formlib.form.FormFields(ITemplateChooserSchema)

    @zope.formlib.form.action(_("Continue"))
    def handle_choose_template(self, action, data):
        session = zope.session.interfaces.ISession(self.request)
        session['zeit.content.article.browser.form']['template'] = data[
            'template']
        url = zope.component.getMultiAdapter(
            (self.context, self.request), name='absolute_url')
        self.request.response.redirect(
            '%s/@@zeit.content.article.Add' % url)


class ArticleFormBase(object):

    field_groups = zeit.cms.browser.form.metadataFieldGroups

    @property
    def template(self):
        # Sneak in the javascript for copying teaser texts
        zc.resourcelibrary.need('zeit.content.article.teaser')
        return super(ArticleFormBase, self).template


class AddForm(ArticleFormBase, zeit.cms.browser.form.AddForm):

    title = _('Add article')
    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.content.article.interfaces.IArticleMetadata,
            omit_readonly=False).omit('textLength') +
        zope.formlib.form.Fields(ITemplateChooserSchema))

    content_template = None

    def create(self, data):
        source = None
        template = data.get('template')
        if template:
            source = StringIO.StringIO(
                zeit.cms.content.interfaces.IXMLSource(template))
        del data['template']
        article = zeit.content.article.article.Article(source)
        self.applyChanges(article, data)
        return article

    def _get_widgets(self, form_fields, ignore_request=False):
        session = zope.session.interfaces.ISession(self.request)
        template = session['zeit.content.article.browser.form'].get(
            'template')
        widgets = super(AddForm, self)._get_widgets(form_fields, ignore_request)

        if not ignore_request and template:
            adapters = {}
            for widget in widgets:
                field = widget.context
                name = widget.context.__name__
                form_field = self.form_fields[name]

                # Adapt context, if necessary
                interface = form_field.interface
                if interface == ITemplateChooserSchema:
                    value = template
                else:
                    adapter = adapters.get(interface)
                    if adapter is None:
                        if interface is None:
                            adapter = template
                        else:
                            adapter = interface(template)
                        adapters[interface] = adapter
                    value = field.get(adapter)
                if value and value != field.default:
                    widget.setRenderedValue(value)

        return widgets


class EditForm(ArticleFormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit article')
    form_fields = zope.formlib.form.Fields(
        zeit.content.article.interfaces.IArticleMetadata,
        render_context=True, omit_readonly=False).omit('textLength')


class DisplayForm(ArticleFormBase, zeit.cms.browser.form.DisplayForm):

    form_fields = (
        zope.formlib.form.Fields(
            zeit.content.article.interfaces.IArticleMetadata,
            render_context=True, omit_readonly=False) +
        zope.formlib.form.Fields(
            zeit.content.article.interfaces.IArticle).select(
                'syndicationLog'))
