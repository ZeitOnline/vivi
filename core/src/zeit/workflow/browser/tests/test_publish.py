import transaction
import zeit.cms.testing
import zeit.workflow.testing
import zope.component.hooks


class TestPublish(zeit.cms.testing.SeleniumTestCase,
                  zeit.workflow.testing.RemoteTaskHelper):

    layer = zeit.workflow.testing.SELENIUM_LAYER

    def setUp(self):
        super(TestPublish, self).setUp()
        self.start_tasks()
        self.open('/repository/testcontent')

    def tearDown(self):
        self.stop_tasks()
        super(TestPublish, self).tearDown()

    def prepare_content(self, id='http://xml.zeit.de/testcontent'):
        from zeit.workflow.interfaces import IContentWorkflow
        import zeit.cms.interfaces
        content = zeit.cms.interfaces.ICMSContent(id)
        IContentWorkflow(content).urgent = True

    def test_action_should_be_available(self):
        self.selenium.assertElementPresent('link=Publish')

    def test_action_should_open_lightbox(self):
        s = self.selenium
        s.assertElementNotPresent('css=.lightbox')
        s.click('link=Publish')
        s.waitForElementPresent('css=.lightbox')

    def test_non_publishable_should_render_error(self):
        s = self.selenium
        s.click('link=Publish')
        s.waitForTextPresent(
            'Cannot publish since preconditions for publishing are not met.')

    def test_publishable_content_should_be_published(self):
        self.prepare_content()
        s = self.selenium
        s.click('link=Publish')
        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=publish]')
        s.waitForElementNotPresent('css=li.busy[action=publish]')
        s.waitForPageToLoad()

    def test_error_during_publish_should_be_messaged(self):
        import zope.app.appsetup.product
        config = zope.app.appsetup.product._configs
        old_script = config['zeit.workflow']['publish-script']
        config['zeit.workflow']['publish-script'] = 'invalid'
        try:
            self.prepare_content()
            s = self.selenium
            s.click('link=Publish')
            s.waitForElementPresent('css=li.error')
            s.verifyText('css=li.error',
                         'Error during publish/retract: OSError*')
        finally:
            config['zeit.workflow']['publish-script'] = old_script

    def test_opening_dialog_from_folder_view_points_to_content(self):
        # Regression VIV-452
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
        zope.component.hooks.setSite(self.getRootFolder())
        self.repository['other'] = TestContentType()
        self.prepare_content('http://xml.zeit.de/other')
        self.prepare_content('http://xml.zeit.de/testcontent')
        IPublish(self.repository['other']).publish()
        IPublish(self.repository['testcontent']).publish()
        transaction.commit()
        self.open('/repository')
        s = self.selenium
        s.click('xpath=//*[contains(text(), "testcontent")]')
        s.waitForElementPresent('css=#bottomcontent a[title=Retract]')
        s.click('css=#bottomcontent a[title="Additional actions"]')
        s.click('css=#bottomcontent a[title=Retract]')
        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=retract]')
        s.waitForElementNotPresent('css=li.busy[action=retract]')
        s.waitForPageToLoad()
        self.assertFalse(
            IPublishInfo(self.repository['testcontent']).published)
        self.assertTrue(IPublishInfo(self.repository['other']).published)


class TestRetract(zeit.cms.testing.SeleniumTestCase,
                  zeit.workflow.testing.RemoteTaskHelper):

    layer = zeit.workflow.testing.SELENIUM_LAYER

    def setUp(self):
        super(TestRetract, self).setUp()
        self.start_tasks()
        self.publish_info.published = True
        self.open('/repository/testcontent')

    def tearDown(self):
        self.stop_tasks()
        super(TestRetract, self).tearDown()

    @property
    def publish_info(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            content = zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/testcontent')
            return zeit.cms.workflow.interfaces.IPublishInfo(content)

    def test_action_should_not_be_available_on_unpublished_content(self):
        self.publish_info.published = False
        self.open('/repository/testcontent')
        self.selenium.assertElementNotPresent('link=Retract')

    def test_action_should_be_available_on_published_content(self):
        self.selenium.assertElementPresent('link=Retract')

    def test_retract_should_retract_item_and_reload_page(self):
        s = self.selenium
        s.click('css=a[title="Additional actions"]')
        s.click('link=Retract')
        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=retract]')
        s.waitForElementNotPresent('css=li.busy[action=retract]')
        s.waitForPageToLoad()
        self.assertFalse(self.publish_info.published)
