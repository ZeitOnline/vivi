# coding: utf-8
from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.testcontenttype.testcontenttype import TestContentType
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.edit.interfaces import IEditableBody
import lxml.etree
import zeit.content.article.testing
import zeit.push.banner
import zeit.push.interfaces
import zeit.push.testing
import zeit.workflow.testing
import zope.component


class StaticArticlePublisherTest(zeit.push.testing.TestCase):

    def setUp(self):
        super(StaticArticlePublisherTest, self).setUp()
        self.repository['foo'] = zeit.content.article.testing.create_article()
        self.publisher = zeit.push.banner.StaticArticlePublisher(
            'http://xml.zeit.de/foo')

    def test_sets_first_paragraph_and_publishes(self):
        self.assertEqual(
            None, ISemanticChange(self.repository['foo']).last_semantic_change)
        self.publisher.send('mytext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish()
        article = self.repository['foo']
        self.assertEqual(True, IPublishInfo(article).published)
        self.assertNotEqual(
            None, ISemanticChange(article).last_semantic_change)
        self.assertEllipsis(
            '<p...><a href="http://zeit.de/foo">mytext</a></p>',
            lxml.etree.tostring(IEditableBody(article).values()[0].xml))

    def test_regression_handles_unicode(self):
        self.publisher.send(u'mütext', 'http://zeit.de/foo')
        zeit.workflow.testing.run_publish()
        article = self.repository['foo']
        self.assertEllipsis(
            '...m&#252;text...',
            lxml.etree.tostring(IEditableBody(article).values()[0].xml))

    def test_checked_out_already_deletes_from_workingcopy_first(self):
        ICheckoutManager(self.repository['foo']).checkout()
        self.publisher.send('mytext', 'http://zeit.de/foo')

    def test_checked_out_by_somebody_else_steals_lock_first(self):
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('other')
        ICheckoutManager(self.repository['foo']).checkout()
        zope.security.management.endInteraction()
        zeit.cms.testing.create_interaction('zope.user')
        self.publisher.send('mytext', 'http://zeit.de/foo')


class RetractBannerTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.push.testing.ZCML_LAYER

    def setUp(self):
        super(RetractBannerTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            for name in ['homepage', 'ios-legacy', 'wrapper']:
                content = TestContentType()
                self.repository[name] = content
                notifier = zope.component.getUtility(
                    zeit.push.interfaces.IPushNotifier, name=name)
                notifier.uniqueId = content.uniqueId

    def tearDown(self):
        for name in ['homepage', 'ios-legacy', 'wrapper']:
            notifier = zope.component.getUtility(
                zeit.push.interfaces.IPushNotifier, name=name)
            del notifier.uniqueId
        super(RetractBannerTest, self).tearDown()

    def test_renders_url_for_each_banner(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/@@breaking-banner-retract')
        self.assertEllipsis("""\
            ...cms:context=".../repository/homepage"...
            ...cms:context=".../repository/ios-legacy"...
            ...cms:context=".../repository/wrapper"...""", b.contents)
