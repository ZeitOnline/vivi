# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.etree
import zeit.cms.content.interfaces
import zeit.cms.testing
import zeit.content.author.author
import zeit.content.author.testing
import zope.component


class AuthorshipXMLReferenceUpdater(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.author.testing.ZCMLLayer

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
