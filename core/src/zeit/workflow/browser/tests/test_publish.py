# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import lovely.remotetask.interfaces
import threading
import zeit.cms.testing
import zeit.workflow.testing
import zope.component


class RemoteTaskHelper(object):

    def start_tasks(self):
        self.tasks = []
        with zeit.cms.testing.site(self.getRootFolder()):
            for name, task in zope.component.getUtilitiesFor(
                lovely.remotetask.interfaces.ITaskService):
                task.startProcessing()
                self.tasks.append(task)

    def stop_tasks(self):
        for task in self.tasks:
            task.stopProcessing()
            self._join_thread(task)

    def _join_thread(self, task):
        # XXX it would be nice if TaskService offered an API to do this
        for thread in threading.enumerate():
            if thread.getName() == task._threadName():
                thread.join()


class TestPublish(zeit.cms.testing.SeleniumTestCase,
                  RemoteTaskHelper):

    layer = zeit.workflow.testing.selenium_layer
    skin = 'vivi'

    def setUp(self):
        super(TestPublish, self).setUp()
        self.start_tasks()
        self.open('/repository/testcontent')

    def tearDown(self):
        self.stop_tasks()
        super(TestPublish, self).tearDown()

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
            s.waitForPageToLoad()
            s.verifyText('css=li.error',
                         'Error during publish/retract: OSError*')
        finally:
            config['zeit.workflow']['publish-script'] = old_script


class TestRetract(zeit.cms.testing.SeleniumTestCase,
                  RemoteTaskHelper):

    layer = zeit.workflow.testing.selenium_layer
    skin = 'vivi'

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
        s.click('link=Retract')
        s.waitForElementPresent('css=ol#worklist')
        s.waitForElementPresent('css=li.busy[action=retract]')
        s.waitForElementNotPresent('css=li.busy[action=retract]')
        s.waitForPageToLoad()
        self.assertFalse(self.publish_info.published)
