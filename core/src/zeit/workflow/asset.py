# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.workflow.interfaces
import zeit.workflow.timebased


class AssetWorkflow(zeit.workflow.timebased.TimeBasedWorkflow):
    """Workflow for assets."""

    zope.interface.implements(zeit.workflow.interfaces.IAssetWorkflow)
    zope.component.adapts(zeit.cms.interfaces.IAsset)

    def can_publish(self):
        return True
