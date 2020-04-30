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

    @property
    def ingredients(self):
        return [Ingredient.from_xml(x) for x in self.xml.xpath('./ingredient')]

    @ingredients.setter
    def ingredients(self, value):
        for node in self.xml.xpath('./ingredient'):
            node.getparent().remove(node)
            pass
        for item in value:
            self.xml.append(
                E.ingredient(
                    code=item.code,
                    label=item.label,
                    amount=item.amount,
                    unit=item.unit))
