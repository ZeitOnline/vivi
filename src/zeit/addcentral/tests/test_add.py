# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.testcontenttype.testcontenttype import TestContentType
import zeit.addcentral.testing
import zeit.cms.browser.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.publisher.browser


class ContentAdderTest(zeit.addcentral.testing.FunctionalTestCase):

    def setUp(self):
        super(ContentAdderTest, self).setUp()
        self.request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSSkin)

    def test_parameters_should_be_passed_in_url(self):
        adder = zeit.addcentral.add.ContentAdder(
            self.request, type_=zeit.content.image.interfaces.IImageGroup,
            ressort='wirtschaft', sub_ressort='geldanlage',
            year='2009', month='02')
        self.assertEqual(
            'http://127.0.0.1/repository/wirtschaft/geldanlage/2009-02/'
            '@@zeit.content.image.imagegroup.Add'
            '?form.sub_ressort=41546881df79e17e56a3bf5ff3f447a6'
            '&form.ressort=cb61e5a1d8e82f77f50ce4f86a114006',
            adder())

    def test_sub_ressort_is_optional(self):
        adder = zeit.addcentral.add.ContentAdder(
            self.request, type_=zeit.content.image.interfaces.IImageGroup,
            ressort='wirtschaft', year='2009', month='02')
        self.assertEqual(
            'http://127.0.0.1/repository/wirtschaft/2009-02/'
            '@@zeit.content.image.imagegroup.Add'
            '?form.ressort=cb61e5a1d8e82f77f50ce4f86a114006',
            adder())

    def test_ressort_and_sub_ressort_are_optional(self):
        adder = zeit.addcentral.add.ContentAdder(
            self.request, type_=zeit.content.image.interfaces.IImageGroup,
            year='2009', month='02')
        self.assertEqual(
            'http://127.0.0.1/repository/2009-02/'
            '@@zeit.content.image.imagegroup.Add?', adder())

    def test_add_location_can_be_overriden_with_adapter(self):
        from zeit.cms.repository.folder import Folder
        self.repository['foo'] = Folder()

        zope.component.getSiteManager().registerAdapter(
            lambda *args: self.repository['foo'],
            (zeit.content.image.interfaces.IImageGroup,
             zeit.addcentral.interfaces.IContentAdder),
            zeit.addcentral.interfaces.IAddLocation)
        adder = zeit.addcentral.add.ContentAdder(
            self.request, type_=zeit.content.image.interfaces.IImageGroup)
        self.assertEqual(
            'http://127.0.0.1/repository/foo/'
            '@@zeit.content.image.imagegroup.Add?', adder())


class RessortYearFolderTest(zeit.addcentral.testing.FunctionalTestCase):

    def test_existing_folder(self):
        from zeit.cms.repository.folder import Folder
        self.repository['wirtschaft'] = Folder()
        self.repository['wirtschaft']['2009-02'] = Folder()
        ANY = None
        adder = zeit.addcentral.add.ContentAdder(
            ANY, ressort='wirtschaft', year='2009', month='2')
        folder = zope.component.getMultiAdapter(
            (TestContentType(), adder),
            zeit.addcentral.interfaces.IAddLocation)
        self.assertEqual(self.repository['wirtschaft']['2009-02'], folder)

    def test_non_existing_folder_should_be_created(self):
        ANY = None
        adder = zeit.addcentral.add.ContentAdder(
            ANY, ressort='wirtschaft', year='2009', month='02')
        folder = zope.component.getMultiAdapter(
            (TestContentType(), adder),
            zeit.addcentral.interfaces.IAddLocation)
        self.assertEqual(self.repository['wirtschaft']['2009-02'], folder)


class JavascriptTest(zeit.cms.testing.SeleniumTestCase):

    layer = zeit.addcentral.testing.selenium_layer
    skin = 'vivi'

    def test_adding(self):
        s = self.selenium
        self.open('/')

        # provoke validation error
        s.waitForElementPresent('sidebar.form.type_')
        s.click('sidebar.form.actions.add')
        s.waitForElementPresent('xpath=//ul[@class="errors"]')

        # successful submit
        s.select('sidebar.form.type_', 'Image Group')
        s.select('sidebar.form.ressort', 'International')
        s.waitForElementPresent('xpath=//option[text() = "Meinung"]')
        s.select('sidebar.form.sub_ressort', 'Meinung')
        s.clickAndWait('sidebar.form.actions.add')
        s.assertLocation(
            '*/international/meinung/*-*/@@zeit.content.image.imagegroup.Add*')

        # values should be remembered in the session
        s.assertSelectedLabel('sidebar.form.ressort', 'International')

        # but selecting something else should take preference
        s.select('sidebar.form.type_', 'Folder')
        s.clickAndWait('sidebar.form.actions.add')
        s.assertLocation(
            '*/international/meinung/*-*/@@zeit.cms.repository.folder.Add*')
