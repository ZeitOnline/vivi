import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.cp.interfaces
import zeit.content.cp.testing


class StoryStreamAddTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.ZCML_LAYER

    def test_storystream_can_be_added(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository')
        menu = b.getControl(name='add_menu')
        menu.displayValue = ['StoryStream']
        b.open(menu.value[0])
        b.getControl('File name').value = 'island'
        b.getControl('Title').value = 'Auf den Spuren der Elfen'
        b.getControl('Ressort').displayValue = ['Reisen']
        b.getControl('Daily newsletter').selected = True
        b.getControl(name='form.authors.0.').value = 'Hans Sachs'
        b.getControl(name="form.actions.add").click()

        with zeit.cms.testing.site(self.getRootFolder()):
            cp = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/island')
            self.assertTrue(
                zeit.content.cp.interfaces.IStoryStream.providedBy(cp))
            self.assertEqual('storystream', cp.type)
