# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.cms.testing
import zeit.workflow.testing


class PublishInfoTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.WorkflowLayer

    def test_last_published_by_takes_last_entry_from_objectlog(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        self.assertEqual(None, info.last_published_by)
        info.urgent = True
        IPublish(content).publish()
        zeit.workflow.testing.run_publish()
        self.assertEqual('zope.user', info.last_published_by)
