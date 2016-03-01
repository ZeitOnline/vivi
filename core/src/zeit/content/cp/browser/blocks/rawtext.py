import zeit.cms.browser.view
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.formlib.form
import lxml.etree


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IRawTextBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))


class Display(zeit.cms.browser.view.Base):

    @property
    def raw_code(self):
        return self.context.raw_code or '<code />'
