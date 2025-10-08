from zeit.cms.content.interfaces import IUUID
from zeit.cms.interfaces import ICMSContent
import zeit.cms.testing


class ContentUUIDTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_use_short_uuid_to_get_content(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        short_uuid = IUUID(content).shortened
        content_from_short_uuid = ICMSContent(IUUID(short_uuid))
        assert content_from_short_uuid == content
