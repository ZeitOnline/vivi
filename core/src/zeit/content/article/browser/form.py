# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import zc.resourcelibrary

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.content.article.interfaces


class ArticleFormBase(object):

    field_groups = zeit.cms.browser.form.metadataFieldGroups

    @property
    def template(self):
        # Sneak in the javascript for copying teaser texts
        zc.resourcelibrary.need('zeit.content.article.teaser')
        return super(ArticleFormBase, self).template


class AddForm(ArticleFormBase, zeit.cms.browser.form.AddForm):

    form_fields = (
        zope.formlib.form.Fields(
            zeit.cms.interfaces.ICMSContent,
            omit_readonly=False).omit('uniqueId') +
        zope.formlib.form.Fields(
            zeit.content.article.interfaces.IArticleMetadata,
            omit_readonly=False).omit('textLength'))

    factory = zeit.content.article.article.Article


class EditForm(ArticleFormBase, zeit.cms.browser.form.EditForm):

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
