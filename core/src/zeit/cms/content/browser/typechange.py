
import zope.component

import zeit.cms.browser.menu
import zeit.cms.interfaces
import zeit.cms.browser.view
import zeit.connector.interfaces
from zeit.cms.i18n import MessageFactory as _


class TypeChange(zeit.cms.browser.view.Base):

    changed = False
    adapters = ()

    def update(self):
        if 'form.actions.changetype' in self.request:
            self.change_type()
        if not self.changed:
            self.create_adapters()

    def change_type(self):
        new_type = self.request.get('newtype')
        if not new_type:
            return
        resource = zeit.connector.interfaces.IResource(self.context)
        connector = zope.component.getUtility(
            zeit.connector.interfaces.IConnector)
        connector.changeProperties(
            resource.id, {
                zeit.connector.interfaces.RESOURCE_TYPE_PROPERTY: new_type
            })
        self.changed = True

    def create_adapters(self):
        resource = zeit.connector.interfaces.IResource(self.context)
        self.adapters = []
        for name, adapter in zope.component.getAdapters(
                (resource, ), zeit.cms.interfaces.ICMSContent):
            resource.data.seek(0)
            if not name:
                # This is the generic factory which calls the other factories.
                # We ignore it because we'll get this result through the
                # specialised adapters, too.
                continue
            list_repr = zope.component.queryMultiAdapter(
                (adapter, self.request),
                zeit.cms.browser.interfaces.IListRepresentation)
            if list_repr is None:
                continue
            self.adapters.append({
                'resource_type': name,
                'content': adapter,
                'list_repr': list_repr})
        self.adapters.sort(key=lambda d: d['resource_type'])

    def __call__(self):
        self.update()
        return self.index()


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Type change menu item."""

    title = _('Change type')
