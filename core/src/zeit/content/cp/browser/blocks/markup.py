import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.formlib.form


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IMarkupBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))
    form_fields['text'].custom_widget = zeit.cms.browser.widget.MarkdownWidget

    def setUpWidgets(self, *args, **kw):
        super(EditProperties, self).setUpWidgets(*args, **kw)
        self.widgets['text'].height = 50
