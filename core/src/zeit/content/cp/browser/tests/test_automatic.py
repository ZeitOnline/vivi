import lxml.etree
import zeit.cms.testing
import zeit.content.cp.testing
import zope.testbrowser.testing


class AutomaticEditForm(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(AutomaticEditForm, self).setUp()
        # XXX As long as the "automatic" properties require a special
        # permission, we can't perform the test as the normal user.
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic zmgr:mgrpw')

    def test_stores_properties_in_xml(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        b.getLink('Edit block automatic').click()
        b.getControl('Amount of teasers').value = '5'
        b.getControl('automatic', index=0).displayValue = ['query']
        b.getControl('Raw query').value = 'foo'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction('zope.mgr'):
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                cp = list(wc.values())[0]
                self.assertEllipsis(
                    '<region...count="5" automatic="query"...>...'
                    '<raw_query>foo</raw_query>...',
                    lxml.etree.tostring(cp['lead'].xml, pretty_print=True))
