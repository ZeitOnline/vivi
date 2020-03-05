from zope.cachedescriptors.property import Lazy as cachedproperty
import zeit.content.modules.interfaces
import zope.interface


@zope.interface.implementer(zeit.content.modules.interfaces.IRecipeList)
class RecipeList(zeit.edit.block.Element):

    @cachedproperty
    def name(self):
        return "moep"
