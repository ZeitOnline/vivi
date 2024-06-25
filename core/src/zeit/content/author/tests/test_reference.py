import zope.component

import zeit.cms.content.interfaces
import zeit.content.article.edit.author
import zeit.content.author.author
import zeit.content.author.testing


class RelatedReferenceTest(zeit.content.author.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.repository['testauthor'] = zeit.content.author.author.Author()
        self.author = self.repository['testauthor']
        self.reference_container = zeit.content.article.edit.author.Author(
            self.author, self.author.xml
        )

    def test_author_can_be_adapted_to_IXMLReference(self):
        result = zope.component.getAdapter(
            self.author, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEqual('author', result.tag)
        self.assertEqual(self.author.uniqueId, result.get('href'))

    def test_author_can_be_adapted_to_IReference(self):
        from zeit.content.author.interfaces import IAuthorBioReference

        result = zope.component.getMultiAdapter(
            (self.reference_container, self.author.xml),
            zeit.cms.content.interfaces.IReference,
            name='related',
        )

        result.biography = 'bio'

        self.assertEqual(True, IAuthorBioReference.providedBy(result))
        self.assertEqual('bio', result.xml.find('biography').text)

    def test_hdok_id_is_added(self):
        author = zeit.content.author.author.Author()
        author.honorar_id = 'honorar-id'
        author = self.repository['testauthor'] = author
        result = zope.component.getAdapter(
            author, zeit.cms.content.interfaces.IXMLReference, name='author'
        )
        self.assertEqual('honorar-id', result.get('hdok'))

    def test_empty_hdok_id_does_not_break(self):
        # This test is about objects that existed before create_honorar_entry
        # event handler existed -- once that's there, it's rather impossible to
        # get to this point.
        api = zope.component.getUtility(zeit.content.author.interfaces.IHonorar)
        api.create.return_value = None

        author = zeit.content.author.author.Author()
        self.repository['testauthor'] = author
        result = zope.component.getAdapter(
            self.repository['testauthor'], zeit.cms.content.interfaces.IXMLReference, name='author'
        )
        self.assertEqual('', result.get('hdok'))
