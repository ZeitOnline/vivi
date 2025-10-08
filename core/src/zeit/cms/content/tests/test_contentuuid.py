from zope.copypastemove.interfaces import IObjectCopier, IObjectMover

from zeit.cms.content.interfaces import IUUID
from zeit.cms.interfaces import ICMSContent
import zeit.cms.testing


class ContentUUIDTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_resolve_uuid_to_content(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        uuid = IUUID(content).id
        content_from_uuid = ICMSContent(IUUID(uuid))
        assert content_from_uuid == content

    def test_resolve_short_uuid_to_content(self):
        content = ICMSContent('http://xml.zeit.de/testcontent')
        short_uuid = IUUID(content).shortened
        content_from_short_uuid = ICMSContent(IUUID(short_uuid))
        assert content_from_short_uuid == content

    def test_copy_gets_new_uuid(self):
        IObjectCopier(self.repository['testcontent']).copyTo(self.repository, 'copy')
        self.assertNotEqual(
            IUUID(self.repository['testcontent']).id, IUUID(self.repository['copy']).id
        )

    def test_move_preserves_uuid(self):
        IObjectMover(self.repository['testcontent']).moveTo(self.repository, 'move')
        self.assertEqual(
            IUUID(self.repository['testcontent']).id, IUUID(self.repository['move']).id
        )
