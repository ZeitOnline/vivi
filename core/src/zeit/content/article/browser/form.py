# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import datetime

import zope.formlib.form
import zope.publisher.interfaces.browser
import zope.session.interfaces

import gocept.form.grouped
import zc.resourcelibrary

import zeit.cms.browser.form
import zeit.cms.content.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.content.image.interfaces
import zeit.content.article.interfaces


ITemplateChooserSchema = (
    zeit.cms.content.browser.template.TemplateChooserSchema(
        'Article templates'))


class ChooseTemplate(zeit.cms.content.browser.template.ChooseTemplateForm):
    """Form for choosing the article template."""

    add_view = 'zeit.content.article.Add'
    form_fields = zope.formlib.form.FormFields(ITemplateChooserSchema)


class ArticleFormBase(object):

    field_groups = zeit.cms.browser.form.metadataFieldGroups + (
        gocept.form.grouped.Fields(
            _("Optionen"),
            ('dailyNewsletter', 'boxMostRead', 'commentsAllowed', 'banner'),
            css_class='widgets-float column-left'),)

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IArticleMetadata).omit(
                'textLength') +
        zope.formlib.form.FormFields(zeit.cms.interfaces.ICMSContent) +
        zope.formlib.form.FormFields(zeit.content.image.interfaces.IImages))


    @property
    def template(self):
        # Sneak in the javascript for copying teaser texts
        zc.resourcelibrary.need('zeit.content.article.teaser')
        return super(ArticleFormBase, self).template


class AddForm(ArticleFormBase, zeit.cms.browser.form.AddForm):

    title = _('Add article')
    form_fields = (
        ArticleFormBase.form_fields +
        ChooseTemplate.form_fields).omit('automaticTeaserSyndication')

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
        widgets = super(AddForm, self)._get_widgets(
            form_fields, ignore_request)

        zeit.cms.content.browser.interfaces.ITemplateWidgetSetup(
            self).setup_widgets(
                widgets, ChooseTemplate.add_view, ITemplateChooserSchema,
                ignore_request)

        return widgets


class EditForm(ArticleFormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit article')


class DisplayForm(ArticleFormBase, zeit.cms.browser.form.DisplayForm):

    title = _('View article metadata')
