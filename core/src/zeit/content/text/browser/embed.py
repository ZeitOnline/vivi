from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.i18n import MessageFactory as _
import zeit.cmp.interfaces
import zeit.cms.browser.form
import zeit.content.text.embed
import zeit.content.text.interfaces
import zope.browsermenu.menu
import zope.formlib.form


class FormBase(object):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IEmbed).select('__name__', 'text')


class Add(FormBase, zeit.cms.browser.form.AddForm):

    title = _('Add embed')
    factory = zeit.content.text.embed.Embed


class AddMenuItem(zope.browsermenu.menu.BrowserMenuItem):

    # zope.browsermenu wants to set the permission from the outside (as
    # declared in zcml), but we want to set it ourselves (according to the
    # toggle), so we allow setting it exactly once.
    _permission = None

    def __init__(self, context, request):
        if FEATURE_TOGGLES.find('add_content_permissions'):
            self._permission = 'zeit.content.text.AddEmbed'
        else:
            self._permission = 'zeit.AddContent'
        return super(AddMenuItem, self).__init__(context, request)

    @property
    def permission(self):
        return self._permission

    @permission.setter
    def permission(self, value):
        if not self._permission:
            self._permission = value


class Edit(FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit embed')


class CMPFields(object):

    def __init__(self, context, request):
        super(CMPFields, self).__init__(context, request)
        if FEATURE_TOGGLES.find('embed_cmp_thirdparty'):
            self.form_fields += zope.formlib.form.FormFields(
                zeit.cmp.interfaces.IConsentInfo).select(
                    'has_thirdparty', 'thirdparty_vendors')


class Parameters(CMPFields, FormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit embed parameters')
    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IEmbed,
        zeit.cms.content.interfaces.IMemo).select(
            'render_as_template', 'parameter_definition', 'vivi_css', 'memo',
            'amp_code')


class Display(CMPFields, zeit.cms.browser.form.DisplayForm):

    title = _('View embed')
    form_fields = zope.formlib.form.FormFields(
        zeit.content.text.interfaces.IEmbed,
        zeit.cms.content.interfaces.IMemo)
