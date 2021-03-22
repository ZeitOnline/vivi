import transaction
import zeit.cms.testing
import zeit.content.cp.testing
import zope.security.management


class AutomaticEditForm(zeit.content.cp.testing.BrowserTestCase):

    # XXX As long as the "automatic" properties require a special
    # permission, we can't perform the test as the normal user.
    login_as = 'zmgr:mgrpw'

    def setUp(self):
        super(AutomaticEditForm, self).setUp()
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('zope.mgr')

    def create_automatic_cp(self, browser):
        zeit.content.cp.browser.testing.create_cp(browser)
        browser.open('contents')
        browser.getLink('Edit block automatic').click()
        browser.getControl('Amount of teasers').value = '3'
        # XXX Why does zope.testbrowser not recognize this as a Checkbox?
        browser.getControl(name='form.automatic').displayValue = ['automatic']

    def test_stores_elasticsearch_query_properties_in_xml(self):
        b = self.browser
        self.create_automatic_cp(b)
        b.getControl('Automatic type', index=0).displayValue = [
            'elasticsearch-query']
        b.getControl('Elasticsearch raw query').value = (
            '{"query": {"match_all": {}}}')
        b.getControl('Sort order', index=1).value = 'date:desc'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        cp = list(wc.values())[0]
        self.assertEllipsis(
            """\
<region...count="3" automatic="True" automatic_type="elasticsearch-query"...>...
<elasticsearch_raw_query>{..."match_all": {}...}</elasticsearch_raw_query>...
<elasticsearch_raw_order>date:desc</elasticsearch_raw_order>...""",  # noqa
            zeit.cms.testing.xmltotext(cp['lead'].xml))

    def test_stores_centerpage_properties_in_xml(self):
        # Create centerpage to reference later on
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        b = self.browser
        self.create_automatic_cp(b)
        b.getControl('Automatic type', index=0).displayValue = [
            'centerpage']
        b.getControl(name='form.referenced_cp').value = 'http://xml.zeit.de/cp'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        cp = list(wc.values())[0]
        self.assertEllipsis(
            """\
<region...count="3" automatic="True" automatic_type="centerpage"...>...
<referenced_cp>http://xml.zeit.de/cp</referenced_cp>...""",
            zeit.cms.testing.xmltotext(cp['lead'].xml))

    def test_stores_topicpage_properties_in_xml(self):
        b = self.browser
        self.create_automatic_cp(b)
        b.getControl('Automatic type', index=0).displayValue = [
            'topicpage']
        b.getControl(name='form.referenced_topicpage').value = 'tms-id'
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)

        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        cp = list(wc.values())[0]
        self.assertEllipsis(
            """\
<region...count="3" automatic="True" automatic_type="topicpage"...>...
<referenced_topicpage>tms-id</referenced_topicpage>...""",
            zeit.cms.testing.xmltotext(cp['lead'].xml))

    def test_stores_rss_feed_in_xml(self):
        b = self.browser
        self.create_automatic_cp(b)
        b.getControl('Automatic type', index=0).displayValue = [
            'rss-feed']
        b.getControl(name='form.rss_feed').value = ['zett']
        b.getControl('Apply').click()
        self.assertEllipsis('...Updated on...', b.contents)
        wc = zeit.cms.checkout.interfaces.IWorkingcopy(None)
        cp = list(wc.values())[0]
        self.assertEllipsis(
            """\
<region...count="3" automatic="True" automatic_type="rss-feed"
 rss_feed="zett">...""",
            zeit.cms.testing.xmltotext(cp['lead'].xml))


class TestAutomaticArea(zeit.content.cp.testing.SeleniumTestCase):

    def setUp(self):
        super(TestAutomaticArea, self).setUp()
        teaser = self.create_content('t1', 'Teaser Title')
        cp_with_teaser = self.create_and_checkout_centerpage(
            'cp_with_teaser', contents=[teaser])
        zeit.cms.checkout.interfaces.ICheckinManager(cp_with_teaser).checkin()

        self.cp = self.create_and_checkout_centerpage('cp')
        transaction.commit()
        self.open_centerpage(create_cp=False)

    def test_toggle_automatic_area_switch(self):
        sel = self.selenium
        # At the beginning two unconfigured areas are present
        sel.assertCssCount('css=.block-automatic-off', 0)
        sel.assertCssCount('css=.block-automatic-on', 0)
        sel.assertCssCount('css=.block-automatic-not-possible', 2)
        sel.assertCssCount('css=.type-teaser', 0)
        sel.assertCssCount('css=.type-auto-teaser', 0)

        # Configure first area, so it can be filled automatically
        sel.click('css=.block.type-area .edit-link')
        sel.waitForElementPresent('css=.lightbox')
        sel.waitForElementPresent('id=form.automatic_type')
        sel.select('id=form.automatic_type', 'automatic-area-type-centerpage')
        sel.type('id=form.referenced_cp.url',
                 'http://xml.zeit.de/cp_with_teaser')
        sel.type('id=form.count', 1)
        sel.click(r'css=#tab-0 #form\.actions\.apply')
        sel.click('css=a.CloseButton')

        # One area is unconfigured, the other could load content automatically
        sel.waitForCssCount('css=.block-automatic-off', 1)
        sel.assertCssCount('css=.block-automatic-on', 0)
        sel.assertCssCount('css=.block-automatic-not-possible', 1)
        sel.assertCssCount('css=.type-teaser', 0)
        sel.assertCssCount('css=.type-auto-teaser', 0)

        # Enable automatic mode, creates automatic teaser block
        sel.click('css=.toggle-automatic-link')
        sel.waitForCssCount('css=.block-automatic-off', 0)
        sel.assertCssCount('css=.block-automatic-on', 1)
        sel.assertCssCount('css=.block-automatic-not-possible', 1)
        sel.assertCssCount('css=.type-teaser', 0)
        sel.assertCssCount('css=.type-auto-teaser', 1)

        # Disable automatic mode, materializes automatic teaser block
        sel.click('css=.toggle-automatic-link')
        sel.waitForCssCount('css=.block-automatic-off', 1)
        sel.assertCssCount('css=.block-automatic-on', 0)
        sel.assertCssCount('css=.block-automatic-not-possible', 1)
        sel.assertCssCount('css=.type-teaser', 1)
        sel.assertCssCount('css=.type-auto-teaser', 0)

    def test_form_shows_widgets_according_to_type(self):
        sel = self.selenium
        sel.click('css=.block.type-area .edit-link')
        sel.waitForElementPresent('id=form.automatic_type')

        sel.assertNotVisible('css=.fieldname-referenced_cp')
        sel.select('id=form.automatic_type', 'automatic-area-type-centerpage')
        sel.assertVisible('css=.fieldname-referenced_cp')

    def test_clicking_on_image_toggles_checkbox(self):
        sel = self.selenium
        sel.click('css=.block.type-area .edit-link')
        sel.waitForElementPresent('id=form.automatic_type')

        sel.assertNotChecked('id=form.automatic')
        sel.click('css=.fieldname-automatic .checkbox')
        sel.assertChecked('id=form.automatic')
