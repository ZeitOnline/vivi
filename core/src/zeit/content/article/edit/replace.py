from zeit.content.article.edit.interfaces import IParagraph
import grokcore.component as grok
import zeit.content.article.edit.interfaces


@grok.implementer(zeit.content.article.edit.interfaces.IFindReplace)
class FindReplace(grok.Adapter):
    grok.context(zeit.content.article.edit.interfaces.IEditableBody)

    def replace_all(self, find, replace):
        count = 0
        for block in self.context.values():
            if not IParagraph.providedBy(block):
                continue
            count += block.text.count(find)
            block.text = block.text.replace(find, replace)
        return count
