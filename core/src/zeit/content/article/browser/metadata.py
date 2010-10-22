# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zc.resourcelibrary
import zeit.cms.content.interfaces
import zope.app.pagetemplate
import zope.formlib.form
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
