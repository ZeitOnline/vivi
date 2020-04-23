from lxml.objectify import E
import zeit.content.modules.interfaces
import zope.interface


class Ingredient(object):

    def __init__(self, id, amount):
        self.id = id
        self.amount = amount

    @classmethod
    def from_xml(cls, node):
        return cls(node.get('id'), node.get('amount'))


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
            node.__parent__.remove(node)
        for item in value:
            self.xml.append(E.ingredient(id=item.id, amount=item.amount))
