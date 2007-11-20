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

    widget_groups = (
        (u"Navigation", ('navigation', 'keywords', 'serie'),
            'small-and-tall'),
        (u"Kopf", ('year', 'volume', 'page', 'ressort'), 'medium-float'),
        (u"Optionen", ('dailyNewsletter', 'boxMostRead', 'commentsAllowed',
                       'banner'), 'medium-float'),
        (u"Texte", zeit.cms.browser.form.REMAINING_FIELDS, 'column-left'),
        (u"sonstiges", ('authors', 'copyrights', 'pageBreak',
                        'automaticTeaserSyndication', 'images'),
         'column-right'),
        )

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

    def setUpWidgets(self, ignore_request=False):
        if not ignore_request:
            form = self.request.form
            if not form:
                form['form.year'] = str(datetime.datetime.now().year)
                form['form.volume'] = str(int(  # Strip leading 0
                    datetime.datetime.now().strftime('%W')))
        super(AddForm, self).setUpWidgets(ignore_request)

    def create(self, data):
        return zeit.content.article.article.Article(**data)


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
