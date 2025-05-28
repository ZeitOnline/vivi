from lxml.builder import E
import zope.interface

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.cms.content.property
import zeit.content.modules.interfaces
import zeit.edit.block
import zeit.wochenmarkt.interfaces


class Ingredient:
    def __init__(self, code, label, **kwargs):
        self.code = code
        self.label = label
        self.amount = kwargs.get('amount')
        self.unit = kwargs.get('unit')
        self.details = kwargs.get('details')
        self.plural = kwargs.get('plural')
        # Conform to zeit.cms.content.sources.ObjectSource
        self.id = self.code
        self.title = self.label

    @classmethod
    def from_xml(cls, node):
        code = node.get('code')
        try:
            ingredient = zeit.wochenmarkt.sources.ingredientsSource(None).find(code)
            # These attributes have to be available:
            name = ingredient.name  # This also represents the singular.
            plural = ingredient.plural
        except AttributeError:
            # Take care of insufficient whitelist data e.g. missing entries.
            return None
        return cls(
            code,
            name,
            amount=node.get('amount', ''),
            unit=node.get('unit', ''),
            details=node.get('details', ''),
            plural=plural,
        )


@zope.interface.implementer(zeit.content.modules.interfaces.IRecipeList)
class RecipeList(zeit.edit.block.Element):
    merge_with_previous = zeit.cms.content.property.ObjectPathProperty(
        '.merge_with_previous', zeit.content.modules.interfaces.IRecipeList['merge_with_previous']
    )

    title = zeit.cms.content.property.ObjectPathProperty(
        '.title', zeit.content.modules.interfaces.IRecipeList['title']
    )

    subheading = zeit.cms.content.property.ObjectPathProperty(
        '.subheading', zeit.content.modules.interfaces.IRecipeList['subheading']
    )

    searchable_subheading = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.subheading',
        'searchable',
        zeit.content.modules.interfaces.IRecipeList['searchable_subheading'],
    )

    _complexity = zeit.cms.content.property.ObjectPathProperty(
        '.complexity', zeit.content.modules.interfaces.IRecipeList['complexity']
    )

    _time = zeit.cms.content.property.ObjectPathProperty(
        '.time', zeit.content.modules.interfaces.IRecipeList['time']
    )

    servings = zeit.cms.content.property.ObjectPathProperty(
        '.servings', zeit.content.modules.interfaces.IRecipeList['servings']
    )

    special_ingredient = zeit.cms.content.property.ObjectPathProperty(
        '.special_ingredient', zeit.content.modules.interfaces.IRecipeList['special_ingredient']
    )

    @property
    def complexity(self):
        if self._complexity is None:
            return self._complexity
        if FEATURE_TOGGLES.find('wcm_889_store_special_category_ids'):
            complexity_source = zeit.content.modules.interfaces.RecipeComplexitySource()
            if complexity_source.factory.findId(self._complexity):
                return self._complexity
            elif complexity_source.factory.getTitle(None, self._complexity):
                id = complexity_source.factory.findIdsbyTitle(self._complexity)
                if id:
                    return id[0]
        return self._complexity

    @complexity.setter
    def complexity(self, value):
        self._complexity = value

    @property
    def time(self):
        if self._time is None:
            return self._time
        if FEATURE_TOGGLES.find('wcm_889_store_special_category_ids'):
            time_source = zeit.content.modules.interfaces.RecipeTimeSource()
            if time_source.factory.findId(self._time):
                return self._time
            elif time_source.factory.getTitle(None, self._time):
                id = time_source.factory.findIdsbyTitle(self._time)
                if id:
                    return id[0]
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def ingredients(self):
        ingredients = [Ingredient.from_xml(x) for x in self.xml.xpath('./ingredient')]
        return [i for i in ingredients if i is not None]

    @ingredients.setter
    def ingredients(self, value):
        for node in self.xml.xpath('./ingredient'):
            node.getparent().remove(node)
        for item in value:
            self.xml.append(
                E.ingredient(
                    code=item.code,
                    amount=item.amount if hasattr(item, 'amount') else '',
                    unit=item.unit if hasattr(item, 'unit') else '',
                    details=item.details if hasattr(item, 'details') else '',
                )
            )
