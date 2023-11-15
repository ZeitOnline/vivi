from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.clipboard.interfaces
import zeit.cms.interfaces
import zope.cachedescriptors.property
import zope.component


class InsertMenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):
    """Insert menu item."""

    title = _('Copy from clipboard')
    icon = '/@@/zeit.cms/icons/insert.png'


class InsertLightbox:
    @zope.cachedescriptors.property.Lazy
    def clipboard(self):
        return zeit.cms.clipboard.interfaces.IClipboard(self.request.principal)

    @zope.cachedescriptors.property.Lazy
    def uniqueId(self):
        return self.context.uniqueId


class Insert(zeit.cms.browser.view.Base):
    """Insert object from clipboard into current container."""

    def __call__(self, unique_id):
        source = zeit.cms.interfaces.ICMSContent(unique_id)
        copier = zope.copypastemove.interfaces.IObjectCopier(source)
        new_name = copier.copyTo(self.context)
        new_obj = self.context[new_name]
        self.send_message(
            _(
                '${source} was copied to ${target}.',
                mapping={'source': unique_id, 'target': new_obj.uniqueId},
            )
        )
        self.redirect(self.url(new_obj))
