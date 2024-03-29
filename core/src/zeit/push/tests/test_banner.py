# coding: utf-8
import lxml.etree
import zope.component
import zope.security.management

from zeit.cms.checkout.interfaces import ICheckoutManager
from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.testing
import zeit.content.article.testing
import zeit.push.banner
import zeit.push.testing


class BannerPublisherTest(zeit.push.testing.TestCase):
    def setUp(self):
        super().setUp()
        self.repository['foo'] = zeit.content.article.testing.create_article()
        self.publisher = zeit.push.banner.Push()
        banner_config = zeit.content.rawxml.rawxml.RawXML()
        banner_config.xml = lxml.etree.fromstring('<xml><article_id/></xml>')
        self.repository['banner'] = banner_config

    def test_banner_xml_is_updated_on_push(self):
        self.publisher.send('foo', 'http://xml.zeit.de/foo')
        banner = self.repository['banner']
        self.assertIn('http://xml.zeit.de/foo', zeit.cms.testing.xmltotext(banner.xml))

    def test_banner_utility_is_updated_on_push(self):
        self.publisher.send('foo', 'http://xml.zeit.de/foo')
        banner = zope.component.getUtility(zeit.push.interfaces.IBanner)
        self.assertEqual('http://xml.zeit.de/foo', banner.article_id)
        self.assertEqual(self.repository['foo'], zeit.push.banner.get_breaking_news_article())

    def test_banner_is_published_on_push(self):
        self.publisher.send('foo', 'http://xml.zeit.de/foo')
        publish = IPublishInfo(self.repository['banner'])
        self.assertTrue(publish.published)

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
