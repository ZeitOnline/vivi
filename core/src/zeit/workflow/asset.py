import zeit.cms.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased
import zope.component
import zope.interface


@zope.component.adapter(zeit.cms.interfaces.IAsset)
@zope.interface.implementer(zeit.workflow.interfaces.IAssetWorkflow)
class AssetWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):
    """Workflow for assets."""

    def can_publish(self):
        status = super(AssetWorkflow, self).can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
