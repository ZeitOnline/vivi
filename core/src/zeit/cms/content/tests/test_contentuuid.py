from cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import IUUID
from zeit.cms.interfaces import ICMSContent
import zeit.cms.testing


class ContentUUIDTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_use_short_uuid_to_get_content(self):
        unique_id = 'http://xml.zeit.de/online/2007/01/Somalia'
        with checked_out(ICMSContent(unique_id)):
            pass
        content = ICMSContent(unique_id)
        short_uuid = IUUID(content).shortened
        content_from_short_uuid = ICMSContent(IUUID(short_uuid))
        assert content_from_short_uuid == content
