import zeit.cms.testing
import zeit.content.text.embed
import zeit.content.text.json
import zeit.content.text.testing


class JSONBrowserTest(zeit.content.text.testing.BrowserTestCase):

    def test_add_json(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/2006')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['JSON file']
        b.open(menu.value[0])
        self.assertEllipsis('...Add JSON file...', b.contents)
        b.getControl('File name').value = 'foo'
        b.getControl('Content').value = '{"foo":'
        b.getControl('Add').click()
        self.assertEllipsis('...Unexpected token...', b.contents)

        b.getControl('Content').value = '{"foo": "bar"}'
        b.getControl('Add').click()
        self.assertEllipsis('...Edit JSON file...', b.contents)

        b.getControl('Content').value = '{"changed": "now"}'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        b.getLink('Checkin').click()
        self.assertEllipsis('...<pre>...changed...</pre>...', b.contents)

    def test_validate_against_schema(self):
        self.repository['foo'] = zeit.content.text.json.JSON()
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/foo')
        b.getLink('Checkout').click()
        self.assertEllipsis('...Validate...', b.contents)
        b.getLink('Validate').click()
        b.getControl('url of schema').value = (
            'http://testschema.zeit.de/schema.yaml')
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
