# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest2
import zeit.cms.testing
import zeit.workflow.testing


class TestPublish(zeit.cms.testing.SeleniumTestCase,
                  unittest2.TestCase):

    layer = zeit.workflow.testing.selenium_layer
    skin = 'vivi'

    def setUp(self):
        import zope.component
        import lovely.remotetask.interfaces
        super(TestPublish, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            for name, task in zope.component.getUtilitiesFor(
                lovely.remotetask.interfaces.ITaskService):
                task.startProcessing()
                self.addCleanup(task.stopProcessing)
        self.open('/repository/testcontent')

    def prepare_content(self):
        from zeit.workflow.interfaces import IContentWorkflow
        import zeit.cms.interfaces
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                content = zeit.cms.interfaces.ICMSContent(
                    'http://xml.zeit.de/testcontent')
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
            'Cannot publish since validation rules are violated.')

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
            s.waitForPageToLoad()
            s.verifyText('css=li.error',
                         'Error during publish/retract: OSError*')
        finally:
            config['zeit.workflow']['publish-script'] = old_script
