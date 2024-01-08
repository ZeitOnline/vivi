import json
import uuid

import celery.result
import transaction

import zeit.workflow.interfaces
import zeit.workflow.testing


class PublishJSONTest(zeit.workflow.testing.BrowserTestCase):
    def setUp(self):
        super().setUp()
        self.browser.handleErrors = False

    def call_json(self, url):
        self.browser.open(url)
        return json.loads(self.browser.contents)

    def enable_publish(self, unique_id):
        somalia = zeit.cms.interfaces.ICMSContent(unique_id)
        workflow = zeit.workflow.interfaces.IContentWorkflow(somalia)
        workflow.urgent = True
        transaction.commit()

    def test_negative_can_publish_should_return_error(self):
        result = self.call_json('http://localhost/repository/online/2007/01/Somalia/@@can-publish')
        self.assertEqual(False, result)

        result = self.call_json('http://localhost/repository/online/2007/01/Somalia/@@publish')
        self.assertEqual({'error': 'publish-preconditions-urgent'}, result)

    def test_publish_should_return_job_id(self):
        self.enable_publish('http://xml.zeit.de/online/2007/01/Somalia')
        result = self.call_json('http://localhost/repository/online/2007/01/Somalia/@@can-publish')
        self.assertEqual(True, result)

        result = self.call_json('http://localhost/repository/online/2007/01/Somalia/@@publish')
        self.assertNotEqual(False, result)
        try:
            uuid.UUID(result)
        except ValueError:
            self.fail('a UUID should be returned as job id')
        finally:
            # test isolation, don't potentially leave jobs in the queue
            celery.result.AsyncResult(result).get()

    def test_retract_should_return_job_id(self):
        result = self.call_json('http://localhost/repository/online/2007/01/Somalia/@@retract')
        self.assertNotEqual(False, result)
        try:
            uuid.UUID(result)
        except ValueError:
            self.fail('a UUID should be returned as job id')
        finally:
            # test isolation, don't potentially leave jobs in the queue
            celery.result.AsyncResult(result).get()
