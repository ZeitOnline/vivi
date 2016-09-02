from zeit.cms.checkout.interfaces import ICheckoutManager
import gocept.testing.mock
import lxml.etree
import mock
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.content.author.author
import zeit.content.author.testing
import zope.component


class AuthorshipXMLReferenceUpdater(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCML_LAYER

    def setUp(self):
        super(AuthorshipXMLReferenceUpdater, self).setUp()
        self.shakespeare = zeit.content.author.author.Author()
        self.shakespeare.firstname = 'William'
        self.shakespeare.lastname = 'Shakespeare'
        self.repository['shakespeare'] = self.shakespeare

    def test_location_is_copied(self):
        content = self.repository['testcontent']
        content.authorships = (content.authorships.create(self.shakespeare),)
        content.authorships[0].location = 'London'
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related')
        self.assertEllipsis("""\
<reference...>
  ...
  <title xsi:nil="true"/>
  ...
  <author href="http://xml.zeit.de/shakespeare"...>
    <display_name...>William Shakespeare</display_name>
    <location>London</location>
  </author>
</reference> """, lxml.etree.tostring(reference, pretty_print=True))

    def test_old_author_nodes_are_removed(self):
        andersen = zeit.content.author.author.Author()
        andersen.firstname = 'Hans Christian'
        andersen.lastname = 'Andersen'
        self.repository['andersen'] = andersen

        content = self.repository['testcontent']
        content.authorships = (content.authorships.create(self.shakespeare),)
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related')
        content.authorships = (content.authorships.create(andersen),)
        zeit.cms.content.interfaces.IXMLReferenceUpdater(
            content).update(reference)

        reference = lxml.etree.tostring(reference, pretty_print=True)
        self.assertEllipsis(
            '...<author href="http://xml.zeit.de/andersen"...', reference)
        self.assertNotIn('shakespeare', reference)

    def test_works_with_security(self):
        with zeit.cms.checkout.helper.checked_out(
                self.repository['testcontent'], temporary=False) as co:
            co = zope.security.proxy.ProxyFactory(co)
            co.authorships = (co.authorships.create(self.shakespeare),)
            co.authorships[0].location = 'London'
            reference = zope.component.getAdapter(
                co, zeit.cms.content.interfaces.IXMLReference, name='related')
            self.assertIn(
                'William Shakespeare',
                lxml.etree.tostring(reference, pretty_print=True))

    def test_fills_in_bbb_author_attribute(self):
        andersen = zeit.content.author.author.Author()
        andersen.firstname = 'Hans Christian'
        andersen.lastname = 'Andersen'
        self.repository['andersen'] = andersen

        content = self.repository['testcontent']
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related')
        self.assertNotIn(
            'author=""', lxml.etree.tostring(reference, pretty_print=True))

        content.authorships = (
            content.authorships.create(self.shakespeare),
            content.authorships.create(andersen))
        reference = zope.component.getAdapter(
            content, zeit.cms.content.interfaces.IXMLReference, name='related')
        self.assertEllipsis(
            """<reference...
            author="William Shakespeare;Hans Christian Andersen"...""",
            lxml.etree.tostring(reference, pretty_print=True))

    def test_updater_suppress_errors(self):
        content = ICheckoutManager(self.repository['testcontent']).checkout()
        content.authorships = (content.authorships.create(self.shakespeare),)

        # This error condition cannot be synthesized easily (would need to make
        # an Author lose its metadata so it's treated as
        # PersistentUnknownResource).

        with mock.patch('zeit.content.author.author.Author.display_name',
                        gocept.testing.mock.Property()) as display_name:
            display_name.side_effect = AttributeError()
            with self.assertNothingRaised():
                updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
                    content)
                updater.update(content.xml, suppress_errors=True)


class RelatedReferenceTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCML_LAYER

    def setUp(self):
        super(RelatedReferenceTest, self).setUp()
        self.repository['testauthor'] = zeit.content.author.author.Author()
        self.author = self.repository['testauthor']

    def test_author_can_be_adapted_to_IXMLReference(self):
        result = zope.component.getAdapter(
            self.author,
            zeit.cms.content.interfaces.IXMLReference,
            name='related')
        self.assertEqual('author', result.tag)
        self.assertEqual(self.author.uniqueId, result.get('href'))

    def test_author_can_be_adapted_to_IReference(self):
        from zeit.content.author.interfaces import IAuthorBioReference

        result = zope.component.getMultiAdapter(
            (self.author, self.author.xml),
            zeit.cms.content.interfaces.IReference, name='related')

        result.biography = 'bio'

        self.assertEqual(True, IAuthorBioReference.providedBy(result))
        self.assertEqual('bio', result.xml.biography.text)
