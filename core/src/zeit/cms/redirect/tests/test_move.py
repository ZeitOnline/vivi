from zeit.cms.checkout.helper import checked_out
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import gocept.async.tests
import lxml.etree
import mock
import zeit.cms.testing
import zope.copypastemove.interfaces


class MoveReferencesTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_renaming_referenced_obj_updates_uniqueId_in_referencing_obj(self):
        self.repository['article'] = TestContentType()
        article = self.repository['article']
        self.repository['referencing'] = TestContentType()
        with checked_out(self.repository['referencing']) as co:
            IRelatedContent(co).related = (article,)

        zope.copypastemove.interfaces.IObjectMover(article).moveTo(
            self.repository, 'changed')
        gocept.async.tests.process()
        referencing = self.repository['referencing']
        with mock.patch('zeit.cms.redirect.interfaces.ILookup') as lookup:
            self.assertEqual(
                ['http://xml.zeit.de/changed'],
                [x.uniqueId for x in IRelatedContent(referencing).related])
            self.assertFalse(lookup().find.called)
        self.assertIn(
            'http://xml.zeit.de/changed',
            lxml.etree.tostring(referencing.xml, pretty_print=True))
