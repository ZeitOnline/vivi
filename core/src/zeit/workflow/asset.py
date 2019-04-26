from zeit.cms.i18n import MessageFactory as _
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
        if self.matches_blacklist():
            self.error_messages = (
                _('publish-preconditions-blacklist',
                  mapping=self._error_mapping),)
            return zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        return zeit.cms.workflow.interfaces.CAN_PUBLISH_SUCCESS
