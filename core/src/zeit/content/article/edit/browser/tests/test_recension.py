from zeit.content.article.interfaces import IBookRecensionContainer
import transaction
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.content.article.recension
import zeit.content.article.testing


class RecensionTest(zeit.content.article.testing.SeleniumTestCase):

    def create_recension(self):
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
            transaction.commit()

        s = self.selenium
        s.setTimeout(3600000)
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        fold = 'css=#edit-form-recensions .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)

    def test_recensions_should_be_listed(self):
        self.create_recension()
        s = self.selenium
        s.assertText('css=span.authors', 'William Shakespeare')
        s.assertText('css=span.title', 'Hamlet')
        s.assertText('css=span.publisher', 'Suhrkamp')
        s.assertText('css=span.location', 'Berlin')

    def test_edit_recension_should_happen_in_lightbox(self):
        self.create_recension()
        s = self.selenium
        s.click('css=span.recensionaction a[rel="edit"]')
        s.waitForElementPresent('id=lightbox.form')
        s.type('form.year', '2001')
        s.click('css=#lightbox\.form #form\.actions\.apply')
        s.waitForElementNotPresent('id=lightbox.form')
        s.waitForElementPresent('css=span.year')
        s.waitForText('css=span.year', '2001')

    def test_submitting_for_list_widget_should_work(self):
        self.create_recension()
        s = self.selenium
        s.click('css=span.recensionaction a[rel="edit"]')
        s.waitForElementPresent('id=lightbox.form')
        s.click('name=form.authors.add')
        s.waitForElementPresent('form.authors.1.')
        s.type('form.authors.1.', 'Lord Byron')
        s.click('css=#lightbox\.form #form\.actions\.apply')
        s.waitForElementNotPresent('id=lightbox.form')
        s.waitForText('css=span.authors', '*Byron*')

    def test_add_recension_should_happen_in_lightbox(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia/@@checkout')
        fold = 'css=#edit-form-recensions .fold-link'
        s.waitForElementPresent(fold)
        s.click(fold)
        s.click('jquery=#recensions a:contains(Add new)')
        s.waitForElementPresent('id=lightbox.form')
        s.type('form.authors.0.', 'Lord Byron')
        s.type('form.title', 'Poems')
        s.select('form.category', 'Belletristik')
        s.click('name=form.actions.add')
        s.waitForElementNotPresent('id=lightbox.form')
        s.waitForElementPresent('css=span.title')
        s.assertText('css=span.title', 'Poems')

    def test_removing_recension_should_reload_editor(self):
        self.create_recension()
        s = self.selenium
        s.click('css=span.recensionaction a[rel="remove"]')
        self.wait_for_condition('!zeit.edit.editor.busy')
        s.waitForElementPresent('css=fieldset#recensions')
        s.waitForElementNotPresent('css=fieldset#recensions div.recension')
