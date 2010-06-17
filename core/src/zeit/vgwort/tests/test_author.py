# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.property
import zeit.cms.repository.interfaces
import zeit.content.author.author
import zeit.vgwort.testing
import zope.component


class AuthorTest(zeit.vgwort.testing.TestCase):

    def test_author_references_should_be_copied_to_author_property(self):
        # zeit.vgwort.report uses the fact that the references to author
        # objects are copied to the freetext 'author' webdav property to filter
        # out which content objects to report, so we need to ensure this
        # copying really happens.
        shakespeare = zeit.content.author.author.Author()
        shakespeare.title = 'Sir'
        shakespeare.firstname = 'William'
        shakespeare.lastname = 'Shakespeare'
        shakespeare.vgwortid = 12345
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['shakespeare'] = shakespeare
        shakespeare = repository['shakespeare']
        content = repository['testcontent']
        with zeit.cms.checkout.helper.checked_out(content) as co:
            co.author_references = [shakespeare]
        self.assertEqual((u'William Shakespeare',), content.authors)
