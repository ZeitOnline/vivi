# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import zeit.cms.interfaces
import zeit.cms.workflow.interfaces
import zeit.content.article.testing
import zeit.edit.rule
import zope.component


class WorkflowTest(zeit.content.article.testing.FunctionalTestCase):

    def setUp(self):
        super(WorkflowTest, self).setUp()
        self.article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        self.info = zeit.cms.workflow.interfaces.IPublishInfo(self.article)

        sm = zope.component.getSiteManager()
        self.orig_validator = sm.adapters.lookup(
            (zeit.content.article.interfaces.IArticle,),
            zeit.edit.interfaces.IValidator)

        self.validator = mock.Mock()
        zope.component.provideAdapter(
            self.validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator)

    def tearDown(self):
        zope.component.getSiteManager().unregisterAdapter(
            required=(zeit.content.article.interfaces.IArticle,),
            provided=zeit.edit.interfaces.IValidator)
        zope.component.provideAdapter(
            self.orig_validator,
            adapts=(zeit.content.article.interfaces.IArticle,),
            provides=zeit.edit.interfaces.IValidator)
        super(WorkflowTest, self).tearDown()

    def test_not_urgent_cannot_publish(self):
        self.assertFalse(self.info.urgent)
        self.assertFalse(self.info.can_publish())
        self.assertFalse(self.validator.called)

    def test_validation_passes_can_publish(self):
        self.info.urgent = True
        self.validator().status = None
        self.assertTrue(self.info.can_publish())
        self.validator.assert_called_with(self.article)

    def test_validation_fails_cannot_publish(self):
        self.info.urgent = True
        self.validator().status = zeit.edit.rule.ERROR
        self.assertFalse(self.info.can_publish())
        self.validator.assert_called_with(self.article)


class DivisionTest(zeit.content.article.testing.FunctionalTestCase):

    # See bug #9495

    def get_article_with_paras(self):
        article = self.get_article()
        factory = self.get_factory(article, 'p')
        for _ in range(10):
            factory()
        return article

    def test_article_should_not_mangle_divisions_on_create(self):
        article = self.get_article_with_paras()
        self.assertEqual(1, len(article.xml.body.findall('division')))

    def test_article_should_not_mangle_divisions_on_add_to_repository(self):
        article = self.get_article_with_paras()
        self.repository['article'] = article
        self.assertEqual(
            1, len(self.repository['article'].xml.body.findall('division')))

    def test_article_should_not_mangle_divisions_on_checkin(self):
        from zeit.cms.checkout.helper import checked_out
        article = self.get_article_with_paras()
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(
            1, len(self.repository['article'].xml.body.findall('division')))

    def test_article_without_division_should_get_them_on_checkin(self):
        from zeit.cms.checkout.helper import checked_out
        article = self.get_article_with_paras()
        # mangle the xml
        for p in article.xml.body.division.getchildren():
            article.xml.body.append(p)
        article.xml.body.remove(article.xml.body.division)
        self.repository['article'] = article
        with checked_out(self.repository['article']):
            pass
        self.assertEqual(
            2, len(self.repository['article'].xml.body.findall('division')))
