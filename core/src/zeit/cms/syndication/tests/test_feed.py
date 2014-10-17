from zeit.cms.checkout.helper import checked_out
import gocept.async.tests
import lxml.etree
import mock
import zeit.cms.testing
import zope.copypastemove.interfaces


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
