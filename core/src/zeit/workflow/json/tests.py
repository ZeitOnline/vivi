# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import cjson
import transaction
import zeit.cms.testing
import zeit.workflow.interfaces
import zeit.workflow.tests
import zope.security.management
import zope.testbrowser.testing


class PublishJSONTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.tests.WorkflowLayer
    product_config = zeit.workflow.tests.product_config

    def setUp(self):
        super(PublishJSONTest, self).setUp()
        zope.security.management.endInteraction()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')

    def test_negative_can_publish_should_return_false(self):
        b = self.browser
        b.open('http://localhost/repository/online/2007/01/Somalia/@@publish')
        result = cjson.decode(b.contents)
        self.assertEqual(False, result)

    def test_publish_should_return_job_id(self):
        zeit.cms.testing.create_interaction()
        somalia = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        workflow = zeit.workflow.interfaces.IContentWorkflow(somalia)
        workflow.urgent = True
        transaction.commit()
        zope.security.management.endInteraction()

        b = self.browser
        b.open('http://localhost/repository/online/2007/01/Somalia/@@publish')
        result = cjson.decode(b.contents)
        self.assertNotEqual(False, result)
        try:
            int(result)
        except ValueError:
            self.fail('a job id should be returned')
