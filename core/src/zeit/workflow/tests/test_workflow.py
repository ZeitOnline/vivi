from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.workflow.testing
import zope.interface


class ContentWorkflowTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def test_content_in_blacklisted_folder_should_not_publish(self):
        self.repository['blacklist'] = zeit.cms.repository.folder.Folder()
        self.repository['blacklist']['content'] = ExampleContentType()
        content = self.repository['blacklist']['content']
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertEqual(CAN_PUBLISH_ERROR, workflow.can_publish())

    def test_asset_in_blacklisted_folder_should_not_publish(self):
        self.repository['blacklist'] = zeit.cms.repository.folder.Folder()
        self.repository['blacklist']['content'] = ExampleContentType()
        content = self.repository['blacklist']['content']
        old_implements = list(zope.interface.implementedBy(
            ExampleContentType))
        zope.interface.classImplementsOnly(
            ExampleContentType,
            zeit.cms.interfaces.IAsset,
            zeit.cms.testcontenttype.interfaces.IExampleContentType)
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(content)
        self.assertEqual(CAN_PUBLISH_ERROR, workflow.can_publish())
        zope.interface.classImplementsOnly(ExampleContentType, *old_implements)
