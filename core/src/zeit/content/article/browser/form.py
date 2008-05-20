# Copyright (c) 2007-2008 gocept gmbh & co. kg
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
import zeit.cms.content.browser.form
import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.interfaces
import zeit.wysiwyg.interfaces
from zeit.content.article.i18n import MessageFactory as _

import zeit.content.article.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.interfaces
import zeit.content.infobox.interfaces
import zeit.content.portraitbox.interfaces


ITemplateChooserSchema = (
    zeit.cms.content.browser.template.TemplateChooserSchema(
        'Article templates'))


class ChooseTemplate(zeit.cms.content.browser.template.ChooseTemplateForm):
    """Form for choosing the article template."""

    add_view = 'zeit.content.article.Add'
    form_fields = zope.formlib.form.FormFields(ITemplateChooserSchema)


base = zeit.cms.content.browser.form.CommonMetadataFormBase

class ArticleFormBase(object):

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IArticleMetadata).omit(
                'textLength') +
        zope.formlib.form.FormFields(zeit.cms.interfaces.ICMSContent))

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        base.text_fields,
        gocept.form.grouped.Fields(
            _('misc.'),
            ('authors', 'copyrights',
             'related', 'infobox', 'images',
             'pageBreak', 'paragraphs', 'vg_wort_id',
             'automaticTeaserSyndication', 'template'),
            css_class='column-right'),
        gocept.form.grouped.Fields(
            _("Optionen"),
            ('dailyNewsletter', 'boxMostRead', 'commentsAllowed',
             'banner', 'has_recensions', 'artbox_thema'),
            css_class='widgets-float column-left'))


class AddForm(ArticleFormBase,
              zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add article')
    form_fields = (
        ArticleFormBase.form_fields +
        ChooseTemplate.form_fields).omit('automaticTeaserSyndication',
                                         'paragraphs')

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


class EditForm(ArticleFormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit article')

    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs)
        if not self.context.automaticTeaserSyndication:
            self.form_fields = self.form_fields.omit('automaticTeaserSyndication');


class DisplayForm(ArticleFormBase,
                  zeit.cms.content.browser.form.CommonMetadataDisplayForm):

    title = _('View article metadata')


class WYSIWYGEdit(zeit.cms.browser.form.EditForm):
    """Edit article content using wysiwyg editor."""

    form_fields = (
        zope.formlib.form.FormFields(
            zeit.content.article.interfaces.IArticleMetadata).select(
                'supertitle', 'title', 'byline', 'subtitle') +
        zope.formlib.form.FormFields(
            zeit.wysiwyg.interfaces.IHTMLContent))

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Content'),
            css_class='full-width wide-widgets'),)


class AssetBase(object):
    """Asset form field definitions."""

    form_fields = zope.formlib.form.FormFields(
        zeit.content.image.interfaces.IImages,
        zeit.cms.content.interfaces.IRelatedContent,
        zeit.content.infobox.interfaces.IInfoboxReference,
        zeit.content.portraitbox.interfaces.IPortraitboxReference,
        zeit.content.gallery.interfaces.IGalleryReference,
    )

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Assets and related'),
            'wide-widgets full-width'),
    )


class AssetEdit(AssetBase, zeit.cms.browser.form.EditForm):
    """Form to edit assets."""

    title = _('Edit assets')

class AssetView(AssetBase, zeit.cms.browser.form.DisplayForm):

    title = _('Assets')
