import zeit.content.text.testing
import zeit.cms.testing


class EmbedBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.text.testing.ZCML_LAYER

    def test_add_embed(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/2006')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Embed']
        b.open(menu.value[0])
        self.assertEllipsis('...Add embed...', b.contents)
        b.getControl('File name').value = 'foo.pembed'
        b.getControl('Content').value = 'test'
        b.getControl('Add').click()
        self.assertEllipsis('...Edit embed...', b.contents)

        b.getControl('Content').value = 'changed'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        b.getLink('Checkin').click()
        self.assertEllipsis('...<pre>changed</pre>...', b.contents)
