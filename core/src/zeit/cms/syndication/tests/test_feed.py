from zeit.cms.checkout.helper import checked_out
import lxml.objectify
import mock
import zeit.cms.content.interfaces
import zeit.cms.syndication.feed
import zeit.cms.testing
import zope.copypastemove.interfaces
import zope.interface.verify


class MoveReferencesTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_renaming_referenced_obj_updates_uniqueId_in_referencing_obj(self):
        self.repository['feed'] = zeit.cms.syndication.feed.Feed()
        with checked_out(self.repository['feed']) as co:
            co.insert(0, self.repository['testcontent'])

        zope.copypastemove.interfaces.IObjectMover(
            self.repository['testcontent']).moveTo(self.repository, 'changed')
        feed = self.repository['feed']
        with mock.patch('zeit.cms.redirect.interfaces.ILookup') as lookup:
            self.assertEqual(
                ['http://xml.zeit.de/changed'], [x.uniqueId for x in feed])
            self.assertFalse(lookup().find.called)
        self.assertIn(
            'http://xml.zeit.de/changed',
            zeit.cms.testing.xmltotext(feed.xml))


class FakeEntryTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_fake_entry_object_should_conform_to_ICMSContent(self):
        uniqueId = 'http://xml.zeit.de/fake'
        fake_entry = zeit.cms.syndication.feed.FakeEntry(
            uniqueId, lxml.objectify.E.entry())
        self.assertEqual(uniqueId, fake_entry.uniqueId)
        self.assertEqual('fake', fake_entry.__name__)

    def test_fake_entry_object_should_conform_to_ICommonMetadata(self):
        ANY = ''
        fake_entry = zeit.cms.syndication.feed.FakeEntry(
            ANY, lxml.objectify.E.entry())
        iface = zeit.cms.content.interfaces.ICommonMetadata
        self.assertTrue(zope.interface.verify.verifyObject(iface, fake_entry))

    def test_fake_entry_should_try_to_retrieve_title_attributes(self):
        ANY = ''
        entry = lxml.objectify.XML('<entry><title>fake</title></entry>')
        fake_entry = zeit.cms.syndication.feed.FakeEntry(ANY, entry)
        self.assertEqual(fake_entry.title, 'fake')
