import zope.copypastemove.interfaces
import zope.interface.verify

from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
import zeit.workflow.testing


class PublishInfoTest(zeit.workflow.testing.FunctionalTestCase):
    def test_last_published_by_takes_last_entry_from_objectlog(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        self.assertEqual(None, info.last_published_by)
        info.urgent = True
        IPublish(content).publish(background=False)
        self.assertEqual('zope.user', info.last_published_by)

    def test_provides_interface(self):
        content = self.repository['testcontent']
        info = IPublishInfo(content)
        zope.interface.verify.verifyObject(IPublishInfo, info)


class WorkflowCopyTest(zeit.workflow.testing.FunctionalTestCase):
    def test_publishinfo_is_reset_for_copied_objects(self):
        content = self.repository['testcontent']
        IPublishInfo(content).published = True
        copier = zope.copypastemove.interfaces.IObjectCopier(content)
        new_name = copier.copyTo(self.repository)
        copied = self.repository[new_name]
        self.assertEqual(False, IPublishInfo(copied).published)
