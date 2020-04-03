import zeit.content.modules.interfaces
import zope.interface


@zope.interface.implementer(zeit.content.modules.interfaces.IRecipeList)
class RecipeList(zeit.edit.block.Element):

    name = zeit.cms.content.property.ObjectPathProperty(
        '.name', zeit.content.modules.interfaces.IRecipeList['name'])

    ingredients = zeit.cms.content.property.ObjectPathProperty(
        '.ingredients',
        zeit.content.modules.interfaces.IRecipeList['ingredients'])
