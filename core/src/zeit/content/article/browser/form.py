# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import StringIO
import datetime

import zope.formlib.form

import zc.resourcelibrary

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
