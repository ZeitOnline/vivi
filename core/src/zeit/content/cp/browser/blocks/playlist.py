import zope.formlib.form
import zope.lifecycleevent

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zeit.content.video.interfaces
import zeit.edit.browser.view


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.IPlaylistBlock).omit(
        *list(zeit.content.cp.interfaces.IBlock)
    )


class DropPlaylist(zeit.edit.browser.view.Action):
    """Drop a playlist to a playlist block."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        if not zeit.content.video.interfaces.IPlaylist.providedBy(content):
            raise ValueError(_('Only playlists can be dropped on a playlist block.'))
        self.context.referenced_playlist = content
        zope.lifecycleevent.modified(self.context)
        self.reload()
