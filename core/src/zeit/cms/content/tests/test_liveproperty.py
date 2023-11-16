from unittest import mock
from zeit.cms.content.interfaces import WRITEABLE_ALWAYS
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.connector.interfaces
import zope.component


class TestRemoveOnCheckin(zeit.cms.testing.ZeitCmsTestCase):
    def test_objects_without_properties_should_not_fail(self):
        import zeit.cms.interfaces
        import zope.event
        import zope.interface
        from zeit.cms.checkout.interfaces import BeforeCheckinEvent

        content = mock.Mock()
        content.uniqueId = 'http://xml.zeit.de/foo'
        zope.interface.alsoProvides(content, zeit.cms.interfaces.ICMSContent)
        zope.event.notify(BeforeCheckinEvent(content, mock.Mock(), mock.Mock()))

    def test_non_cms_objects_should_not_fail(self):
        import zope.event
        from zeit.cms.checkout.interfaces import BeforeCheckinEvent

        content = mock.Mock()
        zope.event.notify(BeforeCheckinEvent(content, mock.Mock(), mock.Mock()))


class AlwaysWriteableProperty(zeit.cms.testing.ZeitCmsTestCase):
    def setUp(self):
        super().setUp()
        manager = zope.component.getUtility(zeit.cms.content.interfaces.ILivePropertyManager)
        manager.register_live_property('foo', 'bar', WRITEABLE_ALWAYS)

    def test_is_writeable_in_repository(self):
        content = self.repository['testcontent']
        properties = zeit.connector.interfaces.IWebDAVProperties(content)
        properties[('foo', 'bar')] = 'qux'
        self.assertEqual('qux', properties[('foo', 'bar')])

    def test_is_writeable_in_workingcopy_and_survives_checkin(self):
        content = self.repository['testcontent']
        properties = zeit.connector.interfaces.IWebDAVProperties(content)
        properties[('foo', 'bar')] = 'one'
        with zeit.cms.checkout.helper.checked_out(content) as co:
            wc_properties = zeit.connector.interfaces.IWebDAVProperties(co)
            wc_properties[('foo', 'bar')] = 'two'
        self.assertEqual('two', properties[('foo', 'bar')])
