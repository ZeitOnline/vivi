import zope.formlib.form

import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):
    form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.IQuizBlock).omit(
        'adreload_enabled',  # XXX Should we support this on CPs too?
        *list(zeit.content.cp.interfaces.IBlock),
    )
