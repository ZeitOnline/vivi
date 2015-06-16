from zeit.content.image.testing import create_image_group_with_master_image
import mock
import zeit.cms.testing
import zeit.content.image.testing
import zeit.edit.interfaces
import zeit.edit.rule
import zope.component


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


class ImageGroupPublishTest(zeit.cms.testing.BrowserTestCase):
    """Integration test for zeit.workflow.browser.publish.Publish.

    Checks that adapter to use ValidatingWorkflow was set up correctly.

    """

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_validation_errors_are_displayed_during_publish(self):
        rm = zope.component.getUtility(zeit.edit.interfaces.IRulesManager)
        rules = [rm.create_rule(['error_if(True, "Custom Error")'], 0)]
        with mock.patch.object(zeit.edit.rule.RulesManager, 'rules', rules):
            b = self.browser
            b.open('http://localhost/++skin++vivi/repository/2007/03/group'
                   '/@@publish.html')
        self.assertEllipsis('...Custom Error...', b.contents)


class ImageGroupBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_traversing_thumbnail_yields_images(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                create_image_group_with_master_image()
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository'
               '/group/thumbnail/square/@@raw')
        self.assertEqual('image/jpeg', b.headers['Content-Type'])
