# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.repository.folder import Folder
from zeit.cms.section.interfaces import ISection
from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.cms.checkout.helper
import zeit.cms.section.testing
import zeit.cms.testing
import zope.interface


class ApplyMarkersTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.cms.section.testing.SECTION_LAYER

    def test_adding_content_to_folder_marks_it_with_general_interface(self):
        self.repository['example']['test'] = Folder()
        obj = self.repository['example']['test']
        self.assertTrue(
            zeit.cms.section.testing.IExampleContent.providedBy(obj))
        self.assertFalse(
            zeit.cms.section.testing.IExampleTestcontent.providedBy(obj))

    def test_specific_types_are_marked_with_type_specific_interface(self):
        self.repository['example']['test'] = TestContentType()
        obj = self.repository['example']['test']
        self.assertTrue(
            zeit.cms.section.testing.IExampleContent.providedBy(obj))
        self.assertTrue(
            zeit.cms.section.testing.IExampleTestcontent.providedBy(obj))

    # XXX not supported yet
    # def test_copymove_into_section_adds_markers(self):
    # def test_copymove_away_from_section_removes_markers(self):

    def test_content_is_marked_on_checkout(self):
        # The test setup is a little convoluted, we need to put an object into
        # a folder /without/ it being marked, so we can check that the marking
        # happens during checkout.
        self.repository['folder'] = zeit.cms.repository.folder.Folder()
        self.repository['folder']['test'] = TestContentType()
        # we cannot change the DAV-Properties of an existing folder
        # while it's checked in -- and checking out folders is not supported,
        # so we *replace* the folder object... don't try this at home, folks.
        folder = zeit.cms.repository.folder.Folder()
        zope.interface.alsoProvides(
            folder, zeit.cms.section.testing.IExampleSection)
        self.repository['folder'] = folder

        obj = self.repository['folder']['test']
        self.assertFalse(
            zeit.cms.section.testing.IExampleContent.providedBy(obj))
        self.assertTrue(
            zeit.cms.section.interfaces.IZONContent.providedBy(obj))

        with zeit.cms.checkout.helper.checked_out(
                self.repository['folder']['test']):
            pass
        obj = self.repository['folder']['test']
        self.assertTrue(
            zeit.cms.section.testing.IExampleContent.providedBy(obj))
        self.assertFalse(
            zeit.cms.section.interfaces.IZONContent.providedBy(obj))


class FindSectionTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.cms.section.testing.SECTION_LAYER

    def test_content_not_in_section_yields_repository(self):
        # since the repository provides IZONSection
        self.assertEqual(
            self.repository, ISection(self.repository['testcontent'], None))

    def test_content_inside_section_finds_that_folder(self):
        self.repository['example']['content'] = TestContentType()
        section = ISection(self.repository['example']['content'])
        self.assertEqual(self.repository['example'], section)
