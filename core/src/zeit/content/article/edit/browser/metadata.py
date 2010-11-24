# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.resourcelibrary
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zope.app.pagetemplate
import zope.formlib.form
import zope.formlib.interfaces
import zope.interface
import zope.viewlet.interfaces
import zope.viewlet.viewlet


class Metadata(object):
    """metadata forms view."""


class MetadataForm(zope.formlib.form.SubPageEditForm):

    template = zope.app.pagetemplate.ViewPageTemplateFile('edit.inlineform.pt')

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


class Head(MetadataForm):

    legend = _('Head')
    prefix = 'head'
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'year', 'volume', 'ressort', 'sub_ressort', 'page')

    def render(self):
        result = super(Head, self).render()
        if result:
            result += (
                '<script type="text/javascript">'
                '    zeit.cms.configure_ressort_dropdown("%s.");'
                '</script>') % (self.prefix,)
        return result


class Navigation(MetadataForm):

    legend = _('Navigation')
    prefix = 'navigation'

    # NOTE: keywords have been left out so far as they will be a new mechanism
    # for them.
    # TODO: provide Javascript to convert title to rename_to

    @property
    def form_fields(self):
        form_fields = zope.formlib.form.FormFields(
            zeit.cms.interfaces.ICMSContent,
            zeit.cms.content.interfaces.ICommonMetadata,
            zeit.cms.repository.interfaces.IAutomaticallyRenameable).select(
                'rename_to', '__name__',
                'serie', 'copyrights', 'product_id')
        if zeit.cms.repository.interfaces.IAutomaticallyRenameable(
            self.context).renamable:
            form_fields = form_fields.omit('__name__')
        else:
            form_fields = form_fields.omit('rename_to')
        return form_fields


class Texts(MetadataForm):

    legend = _('Texts')
    prefix = 'texts'
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata).select(
            'supertitle', 'title', 'subtitle', 'teaserTitle', 'teaserText')


class Misc(MetadataForm):

    legend = _('Misc.')
    prefix = 'misc'
    form_fields = zope.formlib.form.FormFields(
        zeit.content.article.interfaces.IArticleMetadata).select(
            'author_references', 'color_scheme', 'layout',
            'commentsAllowed', 'dailyNewsletter', 'foldable', 'minimal_header',
            'countings', 'is_content', 'banner', 'banner_id')

