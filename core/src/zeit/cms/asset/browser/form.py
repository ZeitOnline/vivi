# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Content related forms."""

from zeit.cms.i18n import MessageFactory as _
import gocept.form.grouped
import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.content.browser.interfaces
import zeit.cms.related.interfaces
import zope.app.appsetup.interfaces
import zope.testing.cleanup



class AssetBase(object):
    """Asset form field definitions."""

    form_fields = None

    field_groups = (
        gocept.form.grouped.RemainingFields(
            _('Teaser elements'),
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
    AssetBase.add_asset_interface(zeit.cms.related.interfaces.IRelatedContent)


@zope.component.adapter(zeit.cms.content.browser.interfaces.IAssetViews)
@zope.interface.implementer(zeit.cms.browser.interfaces.IEditViewName)
def asset_edit_view_name(context):
    return 'asset_edit.html'


@zope.component.adapter(zeit.cms.content.browser.interfaces.IAssetViews)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDisplayViewName)
def asset_display_view_name(context):
    return 'asset_view.html'
