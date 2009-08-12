# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.addcentral.testing
import zeit.cms.browser.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.content.image.interfaces
import zope.component
import zope.publisher.browser


class ContentAdderTest(zeit.addcentral.testing.FunctionalTestCase):

    def test_existing_folder(self):
        repos = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repos['wirtschaft'] = zeit.cms.repository.folder.Folder()
        repos['wirtschaft']['2009-02'] = zeit.cms.repository.folder.Folder()
        adder = zeit.addcentral.add.ContentAdder(
            None, ressort='wirtschaft', year='2009', month='2')
        folder = adder.find_or_create_folder()
        self.assertEqual(repos['wirtschaft']['2009-02'], folder)

    def test_non_existing_folder_should_be_created(self):
        repos = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        adder = zeit.addcentral.add.ContentAdder(
            None, ressort='wirtschaft', year='2009', month='02')
        folder = adder.find_or_create_folder()
        self.assertEqual(repos['wirtschaft']['2009-02'], folder)

    def test_url(self):
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSSkin)
        adder = zeit.addcentral.add.ContentAdder(
            request, type_=zeit.content.image.interfaces.IImageGroup,
            ressort='wirtschaft', sub_ressort='geldanlage',
            year='2009', month='02')
        self.assertEqual(
            'http://127.0.0.1/repository/wirtschaft/geldanlage/2009-02/'
            '@@zeit.content.image.imagegroup.Add'
            '?form.sub_ressort=41546881df79e17e56a3bf5ff3f447a6'
            '&form.ressort=cb61e5a1d8e82f77f50ce4f86a114006',
            adder())

        adder = zeit.addcentral.add.ContentAdder(
            request, type_=zeit.content.image.interfaces.IImageGroup,
            ressort='wirtschaft', year='2009', month='02')
        self.assertEqual(
            'http://127.0.0.1/repository/wirtschaft/2009-02/'
            '@@zeit.content.image.imagegroup.Add'
            '?form.ressort=cb61e5a1d8e82f77f50ce4f86a114006',
            adder())
