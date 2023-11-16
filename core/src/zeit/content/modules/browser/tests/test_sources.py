# coding: utf-8
import zeit.content.modules.testing


class SourceAPI(zeit.content.modules.testing.BrowserTestCase):
    def test_units_endpoint_should_return_valid_json(self):
        self.browser.open(
            'http://localhost/@@source?name=' 'zeit.content.modules.interfaces.RecipeUnitsSource'
        )
        self.assert_json(
            [
                {'id': '', 'title': ''},
                {'id': 'stueck', 'title': 'Stück'},
                {'id': 'kg', 'title': 'kg'},
            ]
        )
