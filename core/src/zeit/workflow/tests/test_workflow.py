from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.cms.repository.unknown
import zeit.cms.testcontenttype.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.workflow.asset
import zeit.workflow.testing
import zope.annotation.interfaces
import zope.interface


class AssetWorkflowTests(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.LAYER

    def setUp(self):
        super(AssetWorkflowTests, self).setUp()
        self.old_implements = list(zope.interface.implementedBy(
            zeit.cms.repository.unknown.PersistentUnknownResource))
        zope.interface.classImplementsOnly(
            zeit.cms.repository.unknown.PersistentUnknownResource,
            zeit.cms.interfaces.IAsset,
            zeit.cms.repository.interfaces.IUnknownResource,
            zope.annotation.interfaces.IAttributeAnnotatable)

    def tearDown(self):
        zope.interface.classImplementsOnly(
            zeit.cms.repository.unknown.PersistentUnknownResource,
            *self.old_implements)
        super(AssetWorkflowTests, self).tearDown()

    def test_asset_workflow(self):
        """The asset workflow is also a time based workflow.

        But there are no constraints in regard to when an asset can be
        published.
        """
        somalia = self.repository['online']['2007']['01']['Somalia']
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(somalia)
        assert isinstance(workflow, zeit.workflow.asset.AssetWorkflow)
        assert 'can-publish-success' == workflow.can_publish()
        assert not workflow.published

        # Publish an asset:
        publish = zeit.cms.workflow.interfaces.IPublish(somalia)
        publish.publish(async=False)
        assert workflow.published

        # Retract of course also works:
        publish.retract(async=False)
        assert not workflow.published


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
