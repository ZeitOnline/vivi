# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.testing


class TestRemoveOnCheckin(zeit.cms.testing.FunctionalTestCase):

    def test_objects_without_properties_should_not_fail(self):
        import zeit.cms.interfaces
        import zope.event
        import zope.interface
        from zeit.cms.checkout.interfaces import BeforeCheckinEvent
        content = mock.Mock()
        zope.interface.alsoProvides(content, zeit.cms.interfaces.ICMSContent)
        zope.event.notify(BeforeCheckinEvent(
            content, mock.Mock(), mock.Mock()))

    def test_non_cms_objects_should_not_fail(self):
        import zope.event
        from zeit.cms.checkout.interfaces import BeforeCheckinEvent
        content = mock.Mock()
        zope.event.notify(BeforeCheckinEvent(
            content, mock.Mock(), mock.Mock()))

