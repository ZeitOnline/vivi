# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.browser.lightbox
import zeit.cms.browser.listing
import zeit.cms.browser.menu
import zeit.cms.browser.view
import zeit.cms.clipboard.interfaces
import zope.component
import zope.interface
import zope.proxy
import zope.publisher.interfaces
from zeit.cms.i18n import MessageFactory as _


class ClipListRepresentation(zeit.cms.browser.listing.BaseListRepresentation):

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(zeit.cms.clipboard.interfaces.IClip,
                          zope.publisher.interfaces.IPublicationRequest)

    author = subtitle = byline = ressort = volume = page = year = None
    uniqueId = None
    searchableText = u''

    @property
    def title(self):
        return self.context.title


class ClipDragPane(object):

    @property
    def unique_id(self):
        clipbaord = zeit.cms.clipboard.interfaces.IClipboard(
            self.request.principal)
        tree = zope.component.getMultiAdapter(
            (clipbaord, self.request),
            name='tree.html')
        return tree.getUniqueId(self.context)


class DeleteClip(zeit.cms.browser.view.Base):

    def __call__(self):
        parent = self.context.__parent__
        title = self.context.title
        del parent[self.context.__name__]
        self.send_message(_('"${name}" was removed from the clipboard.',
                            mapping=dict(name=title)))
        self.redirect(self.url(parent))
        return u''


class NotOnClipboardMenuItem(object):

    def render(self):
        if zeit.cms.clipboard.interfaces.IClipboard.providedBy(self.context):
            # Do not render on clipboard
            return u''
        return super(NotOnClipboardMenuItem, self).render()


class DeleteClipMenuItem(NotOnClipboardMenuItem,
                         zeit.cms.browser.menu.ActionMenuItem):
    """MenuItem for deleting clips."""


class RenameClipMenuitem(NotOnClipboardMenuItem,
                         zeit.cms.browser.menu.LightboxActionMenuItem):
    """MenuItem for renaming clips."""


class IRenameSchema(zope.interface.Interface):

    new_name = zope.schema.TextLine(
        title=_('New clip name'))


class Rename(zeit.cms.browser.lightbox.Form):

    title = _('Rename')
    form_fields = zope.formlib.form.FormFields(IRenameSchema)

    def nextURL(self):
        return self.url(self.context)

    def get_data(self):
        return dict(new_name=self.context.title)

    @zope.formlib.form.action(_('Rename'))
    def rename(self, action, data):
        old_name = self.context.title
        new_name = data['new_name']

        self.context.title = new_name
        self.send_message(_('"${old_name}" was renamed to "${new_name}".',
                            mapping=dict(old_name=old_name,
                                         new_name=new_name)))
