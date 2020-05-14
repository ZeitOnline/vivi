import collections
from lxml.objectify import E
import zeit.content.modules.interfaces
import zope.interface


class Ingredient(object):

    def __init__(self, code, label, amount, unit):
        self.code = code
        self.label = label
        self.amount = amount
        self.unit = unit

    @classmethod
    def from_xml(cls, node):
        return cls(
            node.get('code'),
            node.get('label'),
            node.get('amount'),
            node.get('unit'))


@zope.interface.implementer(zeit.content.modules.interfaces.IRecipeList)
class RecipeList(zeit.edit.block.Element):

    name = zeit.cms.content.property.ObjectPathProperty(
        '.name', zeit.content.modules.interfaces.IRecipeList['name'])

    complexity = zeit.cms.content.property.ObjectPathProperty(
        '.complexity',
        zeit.content.modules.interfaces.IRecipeList['complexity'])

    time = zeit.cms.content.property.ObjectPathProperty(
        '.time',
        zeit.content.modules.interfaces.IRecipeList['time'])

    servings = zeit.cms.content.property.ObjectPathProperty(
        '.servings',
        zeit.content.modules.interfaces.IRecipeList['servings'])

    searchable_title = zeit.cms.content.property.ObjectPathProperty(
        '.searchable_title',
        zeit.content.modules.interfaces.IRecipeList['searchable_title'])

    @property
    def ingredients(self):
        return [Ingredient.from_xml(x) for x in self.xml.xpath('./ingredient')]

    @ingredients.setter
    def ingredients(self, value):
        for node in self.xml.xpath('./ingredient'):
            node.getparent().remove(node)
        value = self._remove_duplicates(value)
        for item in value:
            self.xml.append(
                E.ingredient(
                    code=item.code,
                    label=item.label,
                    amount=item.amount,
                    unit=item.unit))

    def _remove_duplicates(self, ingredients):
        result = collections.OrderedDict()
        for ingredient in ingredients:
            if ingredient.code not in result:
                result[ingredient.code] = ingredient
        return result.values()
