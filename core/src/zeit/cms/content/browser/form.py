# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Content related forms."""

import copy

import zope.testing.cleanup

import zope.app.appsetup.interfaces
import zope.app.form.browser.textwidgets

import gocept.form.grouped
import zc.resourcelibrary

import zeit.cms.browser.form
from zeit.cms.i18n import MessageFactory as _



class ShowLimitInputWidget(zope.app.form.browser.textwidgets.TextAreaWidget):

    def __call__(self):
        zc.resourcelibrary.need('zeit.cms.content.validation')
        max_length = self.context.max_length
        result = [
            '<div class="show-input-limit" maxlength="%s"></div>' % max_length,
        super(ShowLimitInputWidget, self).__call__(),
            ('<script type="text/javascript">new zeit.cms.InputValidation('
             '"%s");</script>') % self.name]

        return ''.join(result)


class CommonMetadataFormBase(object):

    navigation_fields = gocept.form.grouped.Fields(
        _("Navigation"),
        ('__name__', 'keywords', 'serie'),
        css_class='column-right')
    head_fields = gocept.form.grouped.Fields(
        _("Head"),
        ('year', 'volume', 'page', 'ressort', 'sub_ressort'),
        css_class='widgets-float column-left')
    text_fields = gocept.form.grouped.Fields(
        _("Texts"),
        ('supertitle', 'byline', 'title', 'subtitle',
         'teaserTitle', 'teaserText',
         'shortTeaserTitle', 'shortTeaserText',
         'hpTeaserTitle', 'hpTeaserText'),
        css_class='wide-widgets column-left')

    field_groups = (
        navigation_fields,
        head_fields,
        text_fields,
        gocept.form.grouped.RemainingFields(
            _("misc."),
            css_class= 'column-right'),
        )
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.syndication.interfaces.IAutomaticMetadataUpdate)

    for_display = False

    def __init__(self, context, request):
        super(CommonMetadataFormBase, self).__init__(context, request)

        if not self.for_display:
            # Change the widgets of the teaser fields
            change_field_names = (
                'teaserText', 'shortTeaserTitle', 'shortTeaserText')
            form_fields = self.form_fields.omit(*change_field_names)
            changed_fields = []
            for field in change_field_names:
                field = copy.copy(self.form_fields[field])
                field.custom_widget = ShowLimitInputWidget
                changed_fields.append(field)
            self.form_fields = form_fields + zope.formlib.form.FormFields(
                *changed_fields)

    @property
    def template(self):
        # Sneak in the javascript for copying teaser texts
        zc.resourcelibrary.need('zeit.cms.content.teaser')
        zc.resourcelibrary.need('zeit.cms.content.dropdown')
        return super(CommonMetadataFormBase, self).template


class CommonMetadataAddForm(CommonMetadataFormBase,
                            zeit.cms.browser.form.AddForm):
    """Add form which contains the common metadata."""


class CommonMetadataEditForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.EditForm):
    """Edit form which contains the common metadata."""


class CommonMetadataDisplayForm(CommonMetadataFormBase,
                             zeit.cms.browser.form.DisplayForm):
    """Display form which contains the common metadata."""

    for_display = True  # omit custom widget w/ js-validation



class AssetBase(object):
    """Asset form field definitions."""

    form_fields = None

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Assets and related'),
            'wide-widgets full-width'),
    )

    @classmethod
    def add_asset_interface(class_, interface):
        new_fields = zope.formlib.form.FormFields(interface)
        if class_.form_fields is None:
            class_.form_fields = new_fields
        else:
            class_.form_fields += new_fields


class AssetEdit(AssetBase, zeit.cms.browser.form.EditForm):
    """Form to edit assets."""

    title = _('Edit assets')

class AssetView(AssetBase, zeit.cms.browser.form.DisplayForm):

    title = _('Assets')



def _clean_asset_interfaces():
    AssetBase.form_fields = None
zope.testing.cleanup.addCleanUp(_clean_asset_interfaces)


@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def register_asset_interface(event):
    AssetBase.add_asset_interface(zeit.cms.content.interfaces.IRelatedContent)
