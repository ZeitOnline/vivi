# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.cms.checkout.interfaces
import zeit.content.article.testing
import zope.component


class RecensionTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super(RecensionTest, self).setUp()
        repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        repository['article'] = zeit.content.article.article.Article()
        manager = zeit.cms.checkout.interfaces.ICheckoutManager(
            repository['article'])
        self.article = manager.checkout()
        transaction.commit()

    def test_sanity_check_that_we_can_set_p_changed(self):
        self.assertFalse(self.article._p_changed)
        self.article._p_changed = True
        self.assertTrue(self.article._p_changed)

    def test_accessing_recension_container_should_not_write(self):
        self.assertFalse(self.article._p_changed)
        zeit.content.article.interfaces.IBookRecensionContainer(self.article)
        self.assertFalse(self.article._p_changed)

    def test_accessing_recension_should_not_write(self):
        recensions = zeit.content.article.interfaces.IBookRecensionContainer(
            self.article)
        recensions.append(zeit.content.article.recension.BookRecension())
        self.article._p_changed = False
        self.assertFalse(self.article._p_changed)
        list(recensions)
        self.assertFalse(self.article._p_changed)
