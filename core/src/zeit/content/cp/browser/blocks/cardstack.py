import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.formlib.form


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.ICardstackBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))
