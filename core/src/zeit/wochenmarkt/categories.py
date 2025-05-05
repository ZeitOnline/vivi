from lxml.builder import E

from zeit.wochenmarkt.sources import RecipeCategory


class RecipeCategories:
    def __get__(self, instance, class_):
        if instance is not None:
            categories = [
                RecipeCategory.from_xml(x)
                for x in (instance.xml.xpath('./head/recipe_categories/category'))
            ]
            return tuple(c for c in categories if c is not None)
        return None

    def __set__(self, instance, value):
        recipe_categories = instance.xml.xpath('./head/recipe_categories')
        if len(recipe_categories) != 0:
            instance.xml.find('head').remove(recipe_categories[0])
        if len(value) > 0:
            el = E.recipe_categories()
            for item in value:
                el.append(E.category(code=item.code))
            instance.xml.find('head').append(el)
