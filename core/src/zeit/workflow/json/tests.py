from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import celery.states
import json
import mock
import transaction
import uuid
import zeit.cms.testing
import zeit.workflow.interfaces
import zeit.workflow.testing
import zope.security.management
import zope.testbrowser.testing


class PublishJSONTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.workflow.testing.CELERY_LAYER

    def setUp(self):
        super(PublishJSONTest, self).setUp()
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
            uuid.UUID(result)
        except ValueError:
            self.fail('a UUID should be returned as job id')

    def test_retract_should_return_job_id(self):
        result = self.call_json(
            'http://localhost/repository/online/2007/01/Somalia/@@retract')
        self.assertNotEqual(False, result)
        try:
            uuid.UUID(result)
        except ValueError:
            self.fail('a UUID should be returned as job id')
