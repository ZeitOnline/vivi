import zeit.content.cp.browser.blocks.block
import zeit.edit.browser.view
import zeit.content.cp.interfaces
import zope.formlib.form


class Refresh(zeit.edit.browser.view.Action):

    def update(self):
        fm = zope.component.getUtility(zeit.content.cp.interfaces.IFeedManager)
        fm.refresh_feed(self.context.url)
        self.reload()


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRSSBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))
