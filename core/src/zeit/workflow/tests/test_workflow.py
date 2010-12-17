# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.workflow.testing


class PermissionTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.workflow.testing.WorkflowLayer

    def test_local_content_should_deny_publish_permission(self):
        from zeit.cms.checkout.helper import checked_out
        import zeit.cms.interfaces
        import zope.security
        with checked_out(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')) as co:
            self.assertFalse(
                zope.security.checkPermission('zeit.workflow.Publish', co))

    def test_user_should_have_publish_permission(self):
        import zeit.cms.interfaces
        import zope.security
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        self.assertTrue(
            zope.security.checkPermission('zeit.workflow.Publish', content))


