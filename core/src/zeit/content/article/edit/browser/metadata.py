# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.content.article.edit.browser.form
import zope.formlib.form
import zope.formlib.interfaces


class Metadata(object):
    """metadata forms view."""

    title = _('Metadata')


class Head(zeit.content.article.edit.browser.form.InlineForm):

    legend = _('Head')
    prefix = 'head'
    undo_description = _('edit metadata (head)')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'year', 'volume', 'ressort', 'sub_ressort', 'page')

    def render(self):
        result = super(Head, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result


class Navigation(zeit.content.article.edit.browser.form.InlineForm):

    legend = _('Navigation')
    prefix = 'navigation'
    undo_description = _('edit metadata (navigation)')

    # TODO: provide Javascript to convert title to rename_to (#8327)

    @property
    def form_fields(self):
        form_fields = zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata,
            zeit.cms.repository.interfaces.IAutomaticallyRenameable,
            render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
                'rename_to', '__name__', 'keywords',
                'serie', 'product_id', 'copyrights')
        if zeit.cms.repository.interfaces.IAutomaticallyRenameable(
            self.context).renamable:
            form_fields = form_fields.omit('__name__')
        else:
            form_fields = form_fields.omit('rename_to')
        return form_fields


class Texts(zeit.content.article.edit.browser.form.InlineForm):

    legend = _('Texts')
    prefix = 'texts'
    undo_description = _('edit metadata (texts)')
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'supertitle', 'title', 'subtitle', 'teaserTitle', 'teaserText')


class Misc(zeit.content.article.edit.browser.form.InlineForm):

    legend = _('Misc.')
    prefix = 'misc'
    undo_description = _('edit metadata (misc)')
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticleMetadata,
        render_context=zope.formlib.interfaces.DISPLAY_UNWRITEABLE).select(
            'author_references', 'color_scheme', 'layout',
            'commentsAllowed', 'dailyNewsletter', 'foldable', 'minimal_header',
            'countings', 'is_content', 'banner', 'banner_id')

    def __call__(self):
        zope.interface.alsoProvides(
            self.request, zeit.cms.browser.interfaces.IGlobalSearchLayer)
        return super(Misc, self).__call__()
