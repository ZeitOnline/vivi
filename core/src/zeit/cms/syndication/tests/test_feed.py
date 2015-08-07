from zeit.cms.checkout.helper import checked_out
import gocept.async.tests
import lxml.etree
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
        gocept.async.tests.process()
        feed = self.repository['feed']
        with mock.patch('zeit.cms.redirect.interfaces.ILookup') as lookup:
            self.assertEqual(
                ['http://xml.zeit.de/changed'], [x.uniqueId for x in feed])
            self.assertFalse(lookup().find.called)
        self.assertIn(
            'http://xml.zeit.de/changed',
            lxml.etree.tostring(feed.xml, pretty_print=True))


class FakeEntryTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_fake_entry_object_should_conform_to_ICommonMetadata(self):
        fake_entry = zeit.cms.syndication.feed.FakeEntry(
            lxml.objectify.E.entry(), 'foo')
        iface = zeit.cms.content.interfaces.ICommonMetadata
        self.assertTrue(zope.interface.verify.verifyObject(iface, fake_entry))

    def test_fake_entry_should_have_uniqueId_and_title_attributes(self):
        uniqueId = 'http://xml.zeit.de/fake'
        entry = lxml.objectify.XML('<entry><title>fake</title></entry>')
        fake_entry = zeit.cms.syndication.feed.FakeEntry(uniqueId, entry)
        self.assertEqual(fake_entry.uniqueId, uniqueId)
        self.assertEqual(fake_entry.title, 'fake')
