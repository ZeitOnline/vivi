import lxml.etree
import zeit.cms.testing
import zeit.content.cp.testing


class AutomaticEditForm(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_stores_properties_in_xml(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('@@edit-metadata.html')
        b.getControl('Amount of teasers').value = '5'
        b.getControl('automatic').selected = True
        b.getControl('Raw query').value = 'foo'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                cp = list(wc.values())[0]
                self.assertEllipsis(
                    '<region...count="5" automatic="True"...>...'
                    '<raw>foo</raw>...',
                    lxml.etree.tostring(cp['lead'].xml, pretty_print=True))
