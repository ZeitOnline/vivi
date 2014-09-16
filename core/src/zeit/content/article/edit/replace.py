from zeit.content.article.edit.interfaces import IParagraph
import grokcore.component as grok
import zeit.content.article.edit.interfaces


class FindReplace(grok.Adapter):

    grok.context(zeit.content.article.edit.interfaces.IEditableBody)
    grok.implements(zeit.content.article.edit.interfaces.IFindReplace)

    def replace_all(self, find, replace):
        for block in self.context.values():
            if not IParagraph.providedBy(block):
                continue
            block.text = block.text.replace(find, replace)
