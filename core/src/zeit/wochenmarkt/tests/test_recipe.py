from zeit.cms.checkout.helper import checked_out
from zeit.wochenmarkt.recipe import IRecipeArticle
import zeit.cms.interfaces
import zeit.wochenmarkt.sources
import zeit.wochenmarkt.testing


class RecipeArticle(zeit.wochenmarkt.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        uid = 'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept'
        self.repository['article'] = zeit.cms.interfaces.ICMSContent(uid)
        self.categories_source = zeit.wochenmarkt.sources.recipeCategoriesSource(None).factory

    def test_recipe_properties_are_stored(self):
        with checked_out(self.repository['article']):
            pass
        recipe = IRecipeArticle(self.repository['article'])
        self.assertEqual(
            ('Vier Rezepte für eine Herdplatte', 'Wurst-Hähnchen', 'Tomaten-Grieß'),
            recipe.titles,
        )
        self.assertEqual(
            ['brathaehnchen', 'bratwurst', 'chicken-nuggets', 'gurke', 'tomate'],
            sorted(recipe.ingredients),
        )
        categories = [category.id for category in recipe.categories]
        self.assertEqual(
            [
                'complexity-easy',
                'complexity-hard',
                'pastagerichte',
                'time-30min',
                'time-90min',
                'wurstiges',
            ],
            sorted(categories),
        )

    def test_empty_property_is_removed(self):
        with checked_out(self.repository['article']) as co:
            for module in co.body.filter_values(zeit.content.modules.interfaces.IRecipeList):
                del co.body[module.__name__]
        self.assertNotIn(
            ('ingredients', 'http://namespaces.zeit.de/CMS/recipe'),
            zeit.connector.interfaces.IWebDAVProperties(self.repository['article']),
        )

    def test_recipe_special_categories_are_updated(self):
        with checked_out(self.repository['article']) as co:
            recipelist = co.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
            for recipe in recipelist:
                recipe.complexity = 'hard'

        recipe = IRecipeArticle(self.repository['article'])
        categories = [category.id for category in recipe.categories]
        self.assertIn('complexity-hard', categories)
        self.assertNotIn('complexity-easy', categories)

    def test_recipe_category_is_added_on_checkin(self):
        ingredients = zeit.wochenmarkt.sources.ingredientsSource(None).factory
        with checked_out(self.repository['article']) as co:
            recipelist = co.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
            for recipe in recipelist:
                recipe.ingredients = [
                    i
                    for i in recipe.ingredients
                    if ingredients.find(None, i.id) and ingredients.find(None, i.id).diet == 'vegan'
                ]

        recipe = IRecipeArticle(self.repository['article'])
        self.assertEqual(7, len(recipe.categories))
        self.assertIn(self.categories_source.find(None, 'vegane-rezepte'), recipe.categories)
        self.assertEqual(
            ('Vier Rezepte für eine Herdplatte', 'Wurst-Hähnchen', 'Tomaten-Grieß'),
            recipe.titles,
        )
        self.assertEqual(['gurke', 'tomate'], sorted(recipe.ingredients))

        # remove category manually, it should not be re-added
        with checked_out(self.repository['article']) as co:
            info = IRecipeArticle(co)
            info.categories = (i for i in info.categories if i.id != 'vegane-rezepte')
        article = self.repository['article']
        categories = [category.id for category in IRecipeArticle(article).categories]
        self.assertNotIn('vegane-rezepte', categories)
        self.assertEqual(6, len(categories))

    def test_recipe_category_is_added_on_checkin_with_multiple_diets(self):
        ingredients = zeit.wochenmarkt.sources.ingredientsSource(None).factory
        with checked_out(self.repository['article']) as co:
            recipelist = co.body.filter_values(zeit.content.modules.interfaces.IRecipeList)
            for recipe in recipelist:
                recipe.ingredients = [
                    i
                    for i in recipe.ingredients
                    if ingredients.find(None, i.id)
                    and ingredients.find(None, i.id).diet in ('vegan', 'vegetarian')
                ] + [ingredients.find(None, 'ei')]
        recipe = IRecipeArticle(self.repository['article'])
        self.assertEqual(7, len(recipe.categories))
        self.assertIn(self.categories_source.find(None, 'vegetarische-rezepte'), recipe.categories)
        self.assertEqual(
            ('Vier Rezepte für eine Herdplatte', 'Wurst-Hähnchen', 'Tomaten-Grieß'),
            recipe.titles,
        )
        self.assertEqual(['ei', 'gurke', 'tomate'], sorted(recipe.ingredients))
