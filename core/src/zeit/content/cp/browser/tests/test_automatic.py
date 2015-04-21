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

    def test_stores_solr_query_properties_in_xml(self):
        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        b.getLink('Edit block automatic').click()
        b.getControl('Amount of teasers').value = '5'
        b.getControl('automatic', index=0).selected = True
        b.getControl('automatic-area-type', index=0).displayValue = ['query']
        b.getControl('Raw query').value = 'foo'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction('zope.mgr'):
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                cp = list(wc.values())[0]
                self.assertEllipsis(
                    """\
<region...count="5" automatic="True" automatic_type="query"...>...
<raw_query>foo</raw_query>...""",
                    lxml.etree.tostring(cp['lead'].xml, pretty_print=True))

    def test_stores_centerpage_properties_in_xml(self):
        # Create centerpage to reference later on
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction('zope.mgr'):
                self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        b.getLink('Edit block automatic').click()
        b.getControl('Amount of teasers').value = '3'
        b.getControl('automatic', index=0).selected = True
        b.getControl('automatic-area-type', index=0).displayValue = [
            'centerpage']
        b.getControl(name='form.referenced_cp').value = 'http://xml.zeit.de/cp'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction('zope.mgr'):
                wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
                cp = list(wc.values())[0]
                self.assertEllipsis(
                    """\
<region...count="3" automatic="True" automatic_type="centerpage"...>...
<referenced_cp>http://xml.zeit.de/cp</referenced_cp>...""",
                    lxml.etree.tostring(cp['lead'].xml, pretty_print=True))
