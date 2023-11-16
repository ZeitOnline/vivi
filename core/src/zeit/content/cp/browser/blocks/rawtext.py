import zeit.cms.browser.view
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.rawtext
import zope.formlib.form


class EditProperties(
    zeit.content.modules.rawtext.EmbedParameterForm, zeit.content.cp.browser.blocks.block.EditCommon
):
    _form_fields = zope.formlib.form.Fields(zeit.content.cp.interfaces.IRawTextBlock).select(
        'text_reference'
    )
    _omit_fields = list(zeit.content.cp.interfaces.IBlock)


class Display(zeit.cms.browser.view.Base):
    pass
