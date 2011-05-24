# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.i18n import MessageFactory as _
import StringIO
import datetime
import gocept.form.grouped
import zc.resourcelibrary
import zeit.cms.browser.form
import zeit.cms.content.browser.form
import zeit.cms.content.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.interfaces
import zeit.content.article.interfaces
import zeit.wysiwyg.interfaces
import zope.app.appsetup.interfaces
import zope.formlib.form
import zope.publisher.interfaces.browser
import zope.session.interfaces


base = zeit.cms.content.browser.form.CommonMetadataFormBase


class ArticleFormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticleMetadata,
        zeit.cms.interfaces.ICMSContent).omit('textLength')

    field_groups = (
        base.navigation_fields,
        base.head_fields,
        base.text_fields,
        gocept.form.grouped.RemainingFields(
            _('misc.'),
            css_class='column-right'),
        base.author_fields,
        gocept.form.grouped.Fields(
            _("Options"),
            base.option_fields.fields + (
                'has_recensions', 'artbox_thema', 'export_cds'),
            css_class='column-right checkboxes'))


class AddForm(ArticleFormBase,
              zeit.cms.content.browser.form.CommonMetadataAddForm):

    title = _('Add article')
    form_fields = ArticleFormBase.form_fields.omit('paragraphs')
    factory = zeit.content.article.article.Article


class EditForm(ArticleFormBase,
               zeit.cms.content.browser.form.CommonMetadataEditForm):

    title = _('Edit article')


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

