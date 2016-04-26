from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import json
import lovely.remotetask.interfaces
import transaction
import zeit.cms.testing
import zeit.workflow.interfaces
import zeit.workflow.testing
import zope.security.management
import zope.testbrowser.testing


class JSONTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def setUp(self):
        super(JSONTestCase, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')
        self.browser.handleErrors = False

    def call_json(self, url):
        zope.security.management.endInteraction()
        self.browser.open(url)
        return json.loads(self.browser.contents)

    def enable_publish(self, unique_id):
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction()
        somalia = zeit.cms.interfaces.ICMSContent(unique_id)
        workflow = zeit.workflow.interfaces.IContentWorkflow(somalia)
        workflow.urgent = True
        transaction.commit()

    def process(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        queue = config['task-queue-%s' % PRIORITY_DEFAULT]
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)
        zeit.cms.testing.create_interaction()
        tasks.process()


class PublishJSONTest(JSONTestCase):

    def test_negative_can_publish_should_return_false(self):
        result = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@can-publish')
        self.assertEqual(False, result)

        result = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@publish')
        self.assertEqual(False, result)

    def test_publish_should_return_job_id(self):
        self.enable_publish('http://xml.zeit.de/online/2007/01/Somalia')
        result = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@can-publish')
        self.assertEqual(True, result)

        result = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@publish')
        self.assertNotEqual(False, result)
        try:
            int(result)
        except ValueError:
            self.fail('a job id should be returned')

    def test_retract_should_return_job_id(self):
        result = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@retract')
        self.assertNotEqual(False, result)
        try:
            int(result)
        except ValueError:
            self.fail('a job id should be returned')


class RemoteTaskTest(JSONTestCase):

    def test_get_status(self):
        self.enable_publish('http://xml.zeit.de/online/2007/01/Somalia')
        job = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@publish')

        status = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia'
            '/@@job-status?job=%s' % job)
        self.assertEqual('queued', status)
        self.process()
        status = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia'
            '/@@job-status?job=%s' % job)
        self.assertEqual('completed', status)
