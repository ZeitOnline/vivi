import zeit.cms.testing
import zeit.content.image.testing


class ImageGroupGhostTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_adding_imagegroup_adds_a_ghost(self):
        b = self.browser
        b.open('http://localhost/++skin++cms/repository/2006/')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['Image group']
        b.open(menu.value[0])
        b.getControl('File name').value = 'new-hampshire'
        b.getControl('Image title').value = 'New Hampshire'
        b.getControl(name='form.copyrights.0..combination_00').value = (
            'ZEIT ONLINE')
        b.getControl(name='form.copyrights.0..combination_01').value = (
            'http://www.zeit.de/')
        b.getControl(name='form.actions.add').click()

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                self.assertEqual(1, len(wc))
