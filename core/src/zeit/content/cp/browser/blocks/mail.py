import zope.formlib.form

import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    block_fields = list(zeit.content.cp.interfaces.IBlock)
    block_fields.remove('title')
    form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.IMailBlock).omit(
        *block_fields
    )
