import grokcore.component as grok
import zeit.content.modules.interfaces
import zeit.cms.content.browser.sources


class SerializeRecipeUnitsSource(zeit.cms.content.browser.sources.SerializeContextualSource):
    grok.context(zeit.content.modules.interfaces.RecipeUnitsSource)

    def __call__(self):
        result = []
        for unit in self.context._get_tree().xpath('//units/unit'):
            item = {'id': unit.get('code'), 'title': unit.get('singular')}
            result.append(item)
        return result
