import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zope.browser.interfaces
import zope.component
import zope.formlib.form


class CPExtraView:

    @property
    def cpextra_title(self):
        if not self.context.cpextra:
            return None
        source = zeit.content.cp.interfaces.ICPExtraBlock['cpextra'].source(
            self.context)
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms)
        return terms.getTerm(self.context.cpextra).title


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.FormFields(
        zeit.content.cp.interfaces.ICPExtraBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))
