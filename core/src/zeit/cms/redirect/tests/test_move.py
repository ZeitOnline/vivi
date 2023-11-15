from unittest import mock
from zeit.cms.checkout.helper import checked_out
from zeit.cms.redirect.interfaces import IRenameInfo
from zeit.cms.related.interfaces import IRelatedContent
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.testing
import zope.copypastemove.interfaces


class MoveTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_renaming_referenced_obj_updates_uniqueId_in_referencing_obj(self):
        self.repository['2007']['article'] = ExampleContentType()
        article = self.repository['2007']['article']
        self.repository['referencing'] = ExampleContentType()
        with checked_out(self.repository['referencing']) as co:
            IRelatedContent(co).related = (article,)

        zope.copypastemove.interfaces.IObjectMover(article).moveTo(self.repository, 'changed')
        referencing = self.repository['referencing']
        with mock.patch('zeit.cms.redirect.interfaces.ILookup') as lookup:
            self.assertEqual(
                ['http://xml.zeit.de/changed'],
                [x.uniqueId for x in IRelatedContent(referencing).related],
            )
            self.assertFalse(lookup().find.called)
        self.assertIn('http://xml.zeit.de/changed', zeit.cms.testing.xmltotext(referencing.xml))

    def test_rename_stores_old_name_on_dav_property(self):
        self.repository['article'] = ExampleContentType()
        zope.copypastemove.interfaces.IObjectMover(self.repository['article']).moveTo(
            self.repository, 'changed'
        )
        article = self.repository['changed']
        self.assertEqual(('http://xml.zeit.de/article',), IRenameInfo(article).previous_uniqueIds)

    def test_renameinfo_has_security_declaration(self):
        # Since the IObjectMover for IRepository is a trusted adapter,
        # we don't usually notice that we need a security declaration for
        # IRenameInfo.
        self.repository['article'] = ExampleContentType()
        wrapped = zope.security.proxy.ProxyFactory(self.repository['article'])
        self.assertEqual((), IRenameInfo(wrapped).previous_uniqueIds)
