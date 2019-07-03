import zeit.cms.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased
import zope.component
import zope.interface


class AssetWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):
    """Workflow for assets."""

    zope.interface.implements(zeit.workflow.interfaces.IAssetWorkflow)
    zope.component.adapts(zeit.cms.interfaces.IAsset)

    def can_publish(self):
        status = super(AssetWorkflow, self).can_publish()
        if status == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR:
            return status
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
