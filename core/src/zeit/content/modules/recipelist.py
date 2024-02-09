from lxml.builder import E
import zope.interface

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

    @classmethod
    def from_xml(cls, node):
        code = node.get('code')
        try:
            ingredient = zope.component.getUtility(
                zeit.wochenmarkt.interfaces.IIngredientsWhitelist
            ).get(code)
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

    complexity = zeit.cms.content.property.ObjectPathProperty(
        '.complexity', zeit.content.modules.interfaces.IRecipeList['complexity']
    )

    time = zeit.cms.content.property.ObjectPathProperty(
        '.time', zeit.content.modules.interfaces.IRecipeList['time']
    )

    servings = zeit.cms.content.property.ObjectPathProperty(
        '.servings', zeit.content.modules.interfaces.IRecipeList['servings']
    )

    special_ingredient = zeit.cms.content.property.ObjectPathProperty(
        '.special_ingredient', zeit.content.modules.interfaces.IRecipeList['special_ingredient']
    )

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
