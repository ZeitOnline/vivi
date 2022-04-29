import zeit.cms.testing
import zeit.content.text.embed
import zeit.content.text.testing


class EmbedBrowserTest(zeit.content.text.testing.BrowserTestCase):

    login_as = 'producer:producerpw'

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

    def test_special_permission_is_required_to_add_embed_via_addcentral(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@addcentral')
        self.assertIn('Embed', b.getControl('Type').displayOptions)

        b = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        b.login('user', 'userpw')
        b.open('http://localhost/++skin++vivi/@@addcentral')
        self.assertNotIn('Embed', b.getControl('Type').displayOptions)

    def test_edit_cmp_fields(self):
        embed = zeit.content.text.embed.Embed()
        embed.text = ''
        self.repository['embed'] = embed
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/embed/@@checkout')
        b.getLink('Edit embed parameters').click()
        b.getControl('Contains thirdparty code').displayValue = ['yes']
        b.getControl('Add Vendors').click()
        b.getControl('Add Vendors').click()
        b.getControl(name='form.thirdparty_vendors.0.').displayValue = [
            'Twitter']
        b.getControl(name='form.thirdparty_vendors.1.').displayValue = [
            'YouTube']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        self.assertEqual(
            ['yes'], b.getControl('Contains thirdparty code').displayValue)
        self.assertEqual(
            ['Twitter'],
            b.getControl(name='form.thirdparty_vendors.0.').displayValue)
        self.assertEqual(
            ['YouTube'],
            b.getControl(name='form.thirdparty_vendors.1.').displayValue)
