# Copyright (c) 2007-2013 gocept gmbh & co. kg
# See also LICENSE.txt
"""Content related forms."""

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.asset.interfaces
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.content.browser.interfaces
import zope.component


class AssetBase(object):
    """Asset form field definitions."""

    field_groups = (
        gocept.form.grouped.Fields(
            _('Badges'), ('badges',), css_class='asset-badges'),
        gocept.form.grouped.RemainingFields(
            _('Teaser elements'),
            'wide-widgets full-width'),
    )

    def __init__(self, *args, **kw):
        super(AssetBase, self).__init__(*args, **kw)
        interfaces = []
        for name, interface in zope.component.getUtilitiesFor(
                zeit.cms.asset.interfaces.IAssetInterface):
            interfaces.append(interface)
        self.form_fields = zope.formlib.form.FormFields(*interfaces)


class AssetEdit(AssetBase, zeit.cms.browser.form.EditForm):
    """Form to edit assets."""

    title = _('Edit assets')


class AssetView(AssetBase, zeit.cms.browser.form.DisplayForm):

    title = _('Assets')


@zope.component.adapter(zeit.cms.content.browser.interfaces.IAssetViews)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def asset_edit_view_name(context):
    return 'asset_edit.html'


@zope.component.adapter(zeit.cms.content.browser.interfaces.IAssetViews)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def asset_display_view_name(context):
    return 'asset_view.html'
