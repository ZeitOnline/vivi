# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.interfaces import IBookRecensionContainer
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.article.recension
import zeit.content.article.testing


class RecensionTest(zeit.content.article.testing.SeleniumTestCase):

    def create_recension(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with zeit.cms.checkout.helper.checked_out(
                    zeit.cms.interfaces.ICMSContent(
                        'http://xml.zeit.de/online/2007/01/Somalia')) as co:
                    recension = zeit.content.article.recension.BookRecension()
                    recension.authors = ['William Shakespeare']
                    recension.title = 'Hamlet'
                    recension.publisher = 'Suhrkamp'
                    recension.location = 'Berlin'
                    recension.category = 'Belletristik'
                    container = IBookRecensionContainer(co)
                    container.append(recension)

        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        s.waitForElementPresent('css=.recension')

    def test_recensions_should_be_listed(self):
        self.create_recension()
        s = self.selenium
        s.assertText('css=dd.authors', 'William Shakespeare')
        s.assertText('css=dd.title', 'Hamlet')
        s.assertText('css=dd.publisher', 'Suhrkamp')
        s.assertText('css=dd.location', 'Berlin')

    def test_edit_recension_should_happen_in_lightbox(self):
        self.create_recension()
        s = self.selenium
        s.click('css=a.RecensionTitle')
        s.waitForElementPresent('id=lightbox.form')
        s.type('form.year', '2001')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('id=lightbox.form')
        s.waitForElementPresent('css=dd.year')
        s.waitForText('css=dd.year', '2001')

    def test_submitting_for_list_widget_should_work(self):
        self.create_recension()
        s = self.selenium
        s.click('css=a.RecensionTitle')
        s.waitForElementPresent('id=lightbox.form')
        s.click('name=form.authors.add')
        s.waitForElementPresent('form.authors.1.')
        s.type('form.authors.1.', 'Lord Byron')
        s.click('form.actions.apply')
        s.waitForElementNotPresent('id=lightbox.form')
        s.waitForText('css=dd.authors', '*Byron*')

    def test_add_recension_should_happen_in_lightbox(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        add_link = 'css=#recensions a:contains(Add new)'
        s.waitForElementPresent(add_link)
        s.click(add_link)
        s.waitForElementPresent('id=lightbox.form')
        s.type('form.authors.0.', 'Lord Byron')
        s.type('form.title', 'Poems')
        s.select('form.category', 'Belletristik')
        s.click('name=form.actions.add')
        s.waitForElementNotPresent('id=lightbox.form')
        s.waitForElementPresent('css=dd.title')
        s.assertText('css=dd.title', 'Poems')
