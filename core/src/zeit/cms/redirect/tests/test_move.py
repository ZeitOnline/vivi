from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.cms.testing
import zope.copypastemove.interfaces


class MoveReferencesTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_renaming_referenced_obj_updates_uniqueId_in_referencing_obj(self):
        self.repository['article'] = TestContentType()
        article = self.repository['article']
        referencing = TestContentType()
        IRelatedContent(referencing).related = (article,)
        self.repository['referencing'] = referencing

        zope.copypastemove.interfaces.IObjectMover(article).moveTo(
            self.repository, 'changed')
        self.assertEqual(
            ['http://xml.zeit.de/changed'],
            [x.uniqueId for x in IRelatedContent(referencing).related])
