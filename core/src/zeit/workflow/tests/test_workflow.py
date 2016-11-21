import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.repository.unknown
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
        publish.publish()
        assert workflow.published

        # Retract of course also works:
        publish.retract()
        assert not workflow.published
