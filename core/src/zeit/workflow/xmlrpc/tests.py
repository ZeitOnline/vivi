# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.workflow.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        layer=zeit.workflow.testing.WorkflowLayer
    )
