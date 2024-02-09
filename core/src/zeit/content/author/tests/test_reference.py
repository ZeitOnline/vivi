from unittest import mock

import gocept.testing.mock
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.checkout.interfaces import ICheckoutManager
import zeit.cms.content.interfaces
import zeit.content.article.edit.author
import zeit.content.author.author
import zeit.content.author.testing


class AuthorshipXMLReferenceUpdater(zeit.content.author.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.shakespeare = zeit.content.author.author.Author()
        self.shakespeare.firstname = 'William'
        self.shakespeare.lastname = 'Shakespeare'
        self.repository['shakespeare'] = self.shakespeare

    def test_location_is_copied(self):
        content = self.repository['testcontent']
        content.authorships = (content.authorships.create(self.shakespeare),)
        content.authorships[0].location = 'London'
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEllipsis(
            """\
<reference...>
  ...
  <title/>
  ...
  <author...href="http://xml.zeit.de/shakespeare"...>
    <display_name...>William Shakespeare</display_name>
    <location>London</location>
  </author>
</reference> """,
            zeit.cms.testing.xmltotext(reference),
        )

    def test_role_is_copied(self):
        content = self.repository['testcontent']
        content.authorships = (content.authorships.create(self.shakespeare),)
        content.authorships[0].role = 'Fotografie'
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEllipsis(
            """\
<reference...>
  ...
  <title/>
  ...
  <author...href="http://xml.zeit.de/shakespeare"...>
    <display_name...>William Shakespeare</display_name>
    <role>Fotografie</role>
  </author>
</reference> """,
            zeit.cms.testing.xmltotext(reference),
        )

    def test_old_author_nodes_are_removed(self):
        andersen = zeit.content.author.author.Author()
        andersen.firstname = 'Hans Christian'
        andersen.lastname = 'Andersen'
        self.repository['andersen'] = andersen

        content = self.repository['testcontent']
        content.authorships = (content.authorships.create(self.shakespeare),)
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        content.authorships = (content.authorships.create(andersen),)
        zeit.cms.content.interfaces.IXMLReferenceUpdater(content).update(reference)

        reference = zeit.cms.testing.xmltotext(reference)
        self.assertEllipsis('...<author...href="http://xml.zeit.de/andersen"...', reference)
        self.assertNotIn('shakespeare', reference)

    def test_works_with_security(self):
        with checked_out(self.repository['testcontent'], temporary=False) as co:
            co = zope.security.proxy.ProxyFactory(co)
            co.authorships = (co.authorships.create(self.shakespeare),)
            co.authorships[0].location = 'London'
            reference = zope.component.getAdapter(
                co, zeit.cms.content.interfaces.IXMLReference, name='related'
            )
            self.assertIn('William Shakespeare', zeit.cms.testing.xmltotext(reference))

    def test_fills_in_bbb_author_attribute(self):
        andersen = zeit.content.author.author.Author()
        andersen.firstname = 'Hans Christian'
        andersen.lastname = 'Andersen'
        self.repository['andersen'] = andersen

        content = self.repository['testcontent']
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertNotIn('author=""', zeit.cms.testing.xmltotext(reference))

        content.authorships = (
            content.authorships.create(self.shakespeare),
            content.authorships.create(andersen),
        )
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related'
        )
        self.assertEllipsis(
            """<reference...
            author="William Shakespeare;Hans Christian Andersen"...""",
            zeit.cms.testing.xmltotext(reference),
        )

    def test_updater_suppress_errors(self):
        content = ICheckoutManager(self.repository['testcontent']).checkout()
        content.authorships = (content.authorships.create(self.shakespeare),)

        # This error condition cannot be synthesized easily (would need to make
        # an Author lose its metadata so it's treated as
        # PersistentUnknownResource).

        with mock.patch(
            'zeit.content.author.author.Author.display_name', gocept.testing.mock.Property()
        ) as display_name:
            display_name.side_effect = AttributeError()
            with self.assertNothingRaised():
                updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(content)
                updater.update(content.xml, suppress_errors=True)


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
        self.assertEqual('bio', result.xml.biography.text)

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
