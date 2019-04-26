import zeit.cms.browser.view
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zeit.content.modules.rawtext
import zope.formlib.form


class EditProperties(
        zeit.content.modules.rawtext.EmbedParameterForm,
        zeit.content.cp.browser.blocks.block.EditCommon):

    _form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRawTextBlock)
    _omit_fields = list(zeit.content.cp.interfaces.IBlock)


class Display(zeit.cms.browser.view.Base):

    @property
    def raw_code(self):
        return self.context.raw_code or '<code />'
