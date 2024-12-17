from unittest import mock

from lxml import etree
import pytest
import transaction
import zope.component

from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.article import Article
from zeit.content.image.imagegroup import ImageGroup
from zeit.retresco.interfaces import ITMS
import zeit.cms.tagging.tag
import zeit.content.image.interfaces
import zeit.newsimport.interfaces
import zeit.newsimport.news
import zeit.newsimport.testing
import zeit.workflow.testing


FIND_IMAGE = 'zeit.newsimport.news.Image.find_existing_content'
NEWS_ARTICLE_UNIQUEID = (
    'http://xml.zeit.de/news/2022-02/02/great-barrier-reef-' 'erneut-von-korallenbleiche-bedroht'
)


class TestNews(zeit.newsimport.testing.FunctionalTestCase):
    def test_news_article_is_published(self):
        article = self.news.publish(self.news.create())
        info = IPublishInfo(article)
        self.assertTrue(info.published)
        self.assertEqual('2021-12-15 09:28:56', info.date_first_released.to_datetime_string())
        self.assertEqual(
            '2021-12-15 09:28:56', info.date_last_published_semantic.to_datetime_string()
        )

    def test_news_article_has_content(self):
        article = self.news.create()
        self.assertEqual('Beispielmeldung Überschrift', article.title)
        self.assertIn('Zwischenüberschrift', article.body.values()[1].text)
        self.assertEqual('topicbox', article.body.values()[2].type)
        self.assertIn('kursive Fettung', article.body.values()[3].text)
        self.assertIn('Positioniertes Bild', article.body.values()[-2].text)
        self.assertIn('© dpa-infocom, dpa:211215-99-389758/5', article.body.values()[-1].text)

    def test_news_article_has_table(self):
        article = self.news.create()
        table = etree.tostring(
            article.body.xml.find('division/box'), pretty_print=True, encoding='unicode'
        )
        self.assertEllipsis('...Tabellen&amp;#xFC;berschrift...', table)
        self.assertEllipsis('...<subtitle>&lt;table...', table)
        self.assertEllipsis('...&lt;td&gt;foo&lt;/td&gt;...', table)

    def test_news_article_has_lists(self):
        article = self.news.create()
        text = article.body.xml.find('division/ol/li').text
        self.assertIn('James Blunt', text)
        self.assertIn('die Welt', text)

    def test_body_should_not_contain_internal_links(self):
        article = self.news.create()
        article_body = etree.tostring(article.body.xml, encoding='unicode')
        self.assertNotIn('urn:newsml:dpa.com:', article_body)

    def test_news_article_supertitle_fallbacks(self):
        entry = self.dpa.get_entries()[2]
        news = zeit.newsimport.news.ArticleEntry(entry)
        self.assertEqual('Handball', news.supertitle)
        del entry['categories'][0:2]
        del news.supertitle
        self.assertEqual('EM', news.supertitle)
        del entry['categories'][0:5]
        del news.supertitle
        self.assertEqual('Deutschland', news.supertitle)
        del entry['categories'][0:3]
        del news.supertitle
        entry['byline'] = 'one last straw'
        self.assertEqual('one last straw', news.supertitle)

    def test_news_article_has_dav_properties(self):
        article = self.news.create()
        self.assertEqual('dpaBY', article.product.id)
        self.assertEqual((('News', None),), article.channels)
        self.assertFalse(article.commentsAllowed)

        dpa_properties = zeit.newsimport.interfaces.IDPANews(article)
        self.assertEqual('urn:newsml:dpa.com:20090101:211215-99-389758', dpa_properties.urn)

    def test_find_existing_article(self):
        urn = 'urn:newsml:dpa.com:20090101:211215-99-389758'
        article = self.news.find_existing_content(urn)
        self.assertFalse(article)

        article = self.news.publish(self.news.create())
        self.connector.search_result = [self.layer['dpa_article_id']]
        article = self.news.find_existing_content(urn)
        self.assertEqual(self.layer['dpa_article_id'], article.uniqueId)

    def test_publish_only_if_pubstatus_usable(self):
        article = self.news.publish(self.news.create())
        info = IPublishInfo(article)
        self.assertTrue(info.published)

        self.connector.search_result = [self.layer['dpa_article_id']]
        article = self.news.retract()
        info = IPublishInfo(article)
        self.assertFalse(info.published)

    def test_news_article_should_have_author(self):
        article = self.news.create()
        self.assertEqual('dpa', article.agencies[0].firstname)

    def test_rubric_config_returns_product_id(self):
        news = zeit.newsimport.news.ArticleEntry(self.dpa.get_entries()[0])
        self.assertEqual('dpaBY', news.product_id)

    def test_update_article(self):
        article = self.news.publish(self.news.create())
        self.assertEqual('Beispielmeldung Überschrift', article.title)
        self.assertEqual(21, len(article.body.values()))

        dpa_properties = zeit.newsimport.interfaces.IDPANews(article)
        version_1 = dpa_properties.version
        self.assertEqual(5, version_1)

        info = IPublishInfo(article)
        date_first_released_1 = info.date_first_released
        date_last_published_semantic_1 = info.date_last_published_semantic
        self.assertEqual('2021-12-15 09:28:56', date_first_released_1.to_datetime_string())
        self.assertEqual('2021-12-15 09:28:56', date_last_published_semantic_1.to_datetime_string())

        entry = self.dpa.get_entries()[0].copy()
        # NOTE add one day, one version and change headline
        entry['version_created'] = '2021-12-16T10:28:56+01:00'
        entry['version'] = 6
        entry['headline'] = 'Beispielmeldung Überschrift Update'

        news = zeit.newsimport.news.ArticleEntry(entry)
        with mock.patch(FIND_IMAGE) as find_img:
            find_img.return_value = ICMSContent(self.layer['dpa_article_id'] + '-image-group/')
            updated_article = news.publish(news.update(article))
        self.assertEqual('Beispielmeldung Überschrift Update', updated_article.title)
        # NOTE this works only, because we did not update the article_html
        self.assertEqual(len(updated_article.body.values()), len(article.body.values()))

        dpa_properties_2 = zeit.newsimport.interfaces.IDPANews(updated_article)
        self.assertGreater(dpa_properties_2.version, version_1)

        info_2 = IPublishInfo(updated_article)
        self.assertEqual(info_2.date_first_released, date_first_released_1)
        self.assertGreater(info_2.date_last_published_semantic, date_last_published_semantic_1)

    def test_update_article_if_updated_timestamp_has_changed(self):
        article = self.news.publish(self.news.create())
        date_last_published_semantic_1 = IPublishInfo(article).date_last_published_semantic
        updated_1 = zeit.newsimport.interfaces.IDPANews(article).updated
        self.assertEqual('2021-12-15 09:28:56', date_last_published_semantic_1.to_datetime_string())
        self.assertEqual('2021-12-15 09:30:03', updated_1.to_datetime_string())

        entry = self.dpa.get_entries()[0].copy()
        entry['updated'] = '2021-12-15T10:30:03Z'  # plus 1 hour
        news = zeit.newsimport.news.ArticleEntry(entry)
        with mock.patch(FIND_IMAGE) as find_img:
            find_img.return_value = ICMSContent(self.layer['dpa_article_id'] + '-image-group/')
            updated_article = news.publish(news.update(article))

        self.assertEqual(
            IPublishInfo(updated_article).date_last_published_semantic,
            date_last_published_semantic_1,
        )
        self.assertGreater(zeit.newsimport.interfaces.IDPANews(updated_article).updated, updated_1)

    def test_no_update_if_same_article(self):
        article = self.news.publish(self.news.create())
        self.assertFalse(self.news.update(article))

    def test_update_article_with_implicitly_retracted_images(self):
        article = self.news.publish(self.news.create())
        image_group = ICMSContent(f'{article.uniqueId}-image-group', None)
        self.assertTrue(IPublishInfo(image_group).published)
        entry = self.dpa.get_entries()[0].copy()
        entry['associations'] = []
        with mock.patch('zeit.newsimport.news.Image.retract') as retract:
            article_new = zeit.newsimport.news.ArticleEntry(entry)
            article_new.update(article)
            self.assertTrue(retract.called)


class TestImage(zeit.newsimport.testing.FunctionalTestCase):
    def test_image_has_content(self):
        entry = self.dpa.get_entries()[-1].copy()
        image_group = zeit.newsimport.news.Image(entry, Article()).create()
        self.assertTrue(image_group.master_image)
        self.assertEqual(
            (
                'Korallen am Great Barrier Reef, die von der Korallenbleiche '
                'betroffen sind, vor der Küste von Cairns.'
            ),
            zeit.content.image.interfaces.IImageMetadata(image_group).caption,
        )
        self.assertEqual(3, zeit.newsimport.interfaces.IDPANews(image_group).version)

    def test_image_is_published(self):
        entry = self.dpa.get_entries()[-1].copy()
        news_image = zeit.newsimport.news.Image(entry, Article())
        image_group = news_image.create()
        published_image = news_image.publish(image_group)

        semantic = ISemanticChange(published_image)
        self.assertEqual('2022-02-02 09:45:31', semantic.last_semantic_change.to_datetime_string())
        self.assertEqual('image.jpeg', image_group.master_image)

    def test_article_has_image(self):
        entry = self.dpa.get_entries()[-1].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        self.assertTrue(article.main_image)
        self.assertTrue(zeit.content.image.interfaces.IImages(article).image)

    def test_no_image_does_not_break(self):
        entry = self.dpa.get_entries()[-1].copy()
        entry['associations'] = []
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        self.assertFalse(article.main_image)

    def test_update_article_image(self):
        entry = self.dpa.get_entries()[-1].copy()
        article = Article()
        article.__name__ = 'myarticle'
        news_image = zeit.newsimport.news.Image(entry, article)
        image_group = news_image.publish(news_image.create())
        first_news = zeit.newsimport.interfaces.IDPANews(image_group)
        first_version = first_news.version
        self.assertEqual(3, first_version)
        entry = self.dpa.get_entries()[-1].copy()
        entry['associations'][0]['version'] = 4
        news_image = zeit.newsimport.news.Image(entry, article)
        with mock.patch(FIND_IMAGE) as find_img:
            find_img.return_value = ICMSContent(
                'http://xml.zeit.de/news/2022-02/02/myarticle-image-group/'
            )
            image = news_image.find_existing_content()
            image_group = news_image.update(image)
        second_news = zeit.newsimport.interfaces.IDPANews(image_group)
        self.assertEqual(ImageGroup, type(image_group))
        self.assertGreater(second_news.version, first_version)
        self.assertEqual('image.jpeg', image_group.master_image)

    def test_update_article_updates_image(self):
        # XXX this test is complicated, but necessary!
        article = self.add_article_with_image()
        image_group = article.main_image.target
        first_news = zeit.newsimport.interfaces.IDPANews(image_group)
        first_version = first_news.version

        # NOTE force article update
        entry = self.dpa.get_entries()[-1].copy()
        entry['version_created'] = '2022-02-03 10:42:18+01:00'
        entry['version'] = 6
        entry['headline'] = 'Great Barrier reef Update'
        entry['associations'][0]['version'] = 4
        news = zeit.newsimport.news.ArticleEntry(entry)
        with mock.patch(FIND_IMAGE) as find_img:
            find_img.return_value = image_group
            updated_article = news.publish(news.update(article))

        updated_image_group = updated_article.main_image.target
        teaser_image = zeit.content.image.interfaces.IImages(updated_article)
        second_news = zeit.newsimport.interfaces.IDPANews(updated_image_group)
        self.assertGreater(second_news.version, first_version)
        self.assertEqual(teaser_image.image, updated_image_group)

    def test_retract_delete_image(self):
        entry = self.dpa.get_entries()[-1].copy()
        article = self.add_article_with_image()
        self.assertTrue(article.main_image.target)
        self.assertTrue(zeit.content.image.interfaces.IImages(article).image)
        news_image = zeit.newsimport.news.Image(entry, article)
        image_group = ICMSContent(f'{article.uniqueId}-image-group', None)
        self.assertTrue(IPublishInfo(image_group).published)
        news_image.delete()
        self.assertFalse(IPublishInfo(image_group).published)
        transaction.commit()
        image_group = ICMSContent(f'{article.uniqueId}-image-group', None)
        self.assertEqual(None, image_group)
        updated_article = ICMSContent(article.uniqueId)
        teaser_image = zeit.content.image.interfaces.IImages(updated_article)
        self.assertFalse(teaser_image.image)

    def test_do_not_delete_non_existing_image(self):
        """
        ZO-1037: This is a failsafe to ensure no exception is raised
        """
        entry = self.dpa.get_entries()[2].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        self.assertFalse(article.main_image.target)
        entry = self.dpa.get_entries()[2].copy()
        entry['version_created'] = '2022-02-08 11:42:18+01:00'
        entry['version'] = 6
        article_new = zeit.newsimport.news.ArticleEntry(entry)
        article_new.update(article)
        self.assertFalse(article.main_image.target)

    def test_create_article_despite_image_download_failure(self):
        entry = self.dpa.get_entries()[-1].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        with mock.patch('zeit.content.image.image.get_remote_image') as image:
            image.return_value = None
            article = news.publish(news.create())
        self.assertTrue(IPublishInfo(article).published)
        self.assertFalse(article.main_image)

    def test_update_article_despite_image_download_failure(self):
        image_group_id = f'{NEWS_ARTICLE_UNIQUEID}-image-group/'

        entry = self.dpa.get_entries()[-1].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        self.assertTrue(2, zeit.newsimport.interfaces.IDPANews(article).version)
        self.assertTrue(3, zeit.newsimport.interfaces.IDPANews(article.main_image.target).version)
        image_group = ICMSContent(image_group_id)
        self.assertTrue(IPublishInfo(image_group).published)
        entry['version_created'] = '2022-02-03T11:42:18+01:00'
        entry['version'] = 6
        entry['associations'][0]['version'] = 4
        entry['associations'][0]['version_created'] = '2022-02-03T10:45:31+01:00'
        self.connector.search_result = [image_group_id]
        with mock.patch('zeit.content.image.image.get_remote_image') as image:
            image.return_value = None
            article = news.publish(news.update(article))
        self.assertTrue(IPublishInfo(article).published)
        self.assertTrue('Great Barrier Reef erneut von Korallenbleiche bedroht', article.title)

    def test_entry_without_article_html_is_image(self):
        entry = self.dpa.get_entries()[3]
        news = zeit.newsimport.news.Entry.from_entry(entry)
        self.assertEqual(zeit.newsimport.news.ImageEntry, type(news))

    def test_image_entry_has_article_context(self):
        entry = self.dpa.get_entries()[-1]
        news = zeit.newsimport.news.ArticleEntry(entry)
        news.publish(news.create())
        entry['article_html'] = None
        entry['urn'] = entry['associations'][0]['urn']
        self.connector.search_result = [f'{NEWS_ARTICLE_UNIQUEID}-image-group/']
        news = zeit.newsimport.news.ImageEntry(entry)
        self.assertEqual(NEWS_ARTICLE_UNIQUEID, news.article_context.uniqueId)

    def test_update_image_without_article_context(self):
        entry = self.dpa.get_entries()[-1]
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())

        image_group = article.main_image.target
        old_version = zeit.newsimport.interfaces.IDPANews(image_group).version
        self.assertEqual(3, old_version)

        # NOTE: Make it an updated image entry without article context
        entry['article_html'] = None
        entry['urn'] = entry['associations'][0]['urn']
        entry['version'] = 4
        entry['version_created'] = '2022-02-03T10:45:31+01:00'  # +1 day
        entry['associations'][0]['version'] = 4
        entry['associations'][0]['version_created'] = '2022-02-03T10:45:31+01:00'  # +1 day

        self.connector.search_result = [f'{NEWS_ARTICLE_UNIQUEID}-image-group/']
        image_entry = zeit.newsimport.news.ImageEntry(entry)
        image_entry.do_import()
        article = ICMSContent(NEWS_ARTICLE_UNIQUEID)
        self.assertGreater(
            zeit.newsimport.interfaces.IDPANews(article.main_image.target).version, old_version
        )

    def test_retract_image_without_article_context(self):
        entry = self.dpa.get_entries()[-1]
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        self.assertTrue(article.main_image.target)

        entry['article_html'] = None
        entry['urn'] = entry['associations'][0]['urn']
        entry['pubstatus'] = 'canceled'
        entry['version'] = entry['associations'][0]['version']
        entry['version_created'] = entry['associations'][0]['version']

        self.connector.search_result = [f'{NEWS_ARTICLE_UNIQUEID}-image-group/']
        image_entry = zeit.newsimport.news.ImageEntry(entry)
        image_entry.retract()
        imagegroup = ICMSContent(f'{NEWS_ARTICLE_UNIQUEID}-image-group/')
        self.assertFalse(IPublishInfo(imagegroup).published)

    def test_non_existend_image_entry_does_not_break(self):
        entry = self.dpa.get_entries()[-1].copy()
        entry['associations'] = []
        news = zeit.newsimport.news.ImageEntry(entry)
        image_group = news.do_import()
        self.assertEqual(None, image_group)

    def test_retract_article_retracts_article_image_group(self):
        image_group_id = f'{NEWS_ARTICLE_UNIQUEID}-image-group/'
        entry = self.dpa.get_entries()[-1].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        image_group = ICMSContent(image_group_id)
        self.assertTrue(IPublishInfo(article).published)
        self.assertTrue(IPublishInfo(image_group).published)

        self.connector.search_result = [article.uniqueId]
        article = news.retract()
        image_group = ICMSContent(image_group_id)
        self.assertFalse(IPublishInfo(article).published)
        self.assertFalse(IPublishInfo(image_group).published)

    def test_retract_article_without_image_does_not_break(self):
        entry = self.dpa.get_entries()[2].copy()
        news = zeit.newsimport.news.ArticleEntry(entry)
        article = news.publish(news.create())
        self.assertTrue(IPublishInfo(article).published)
        self.connector.search_result = [article.uniqueId]
        article = news.retract()
        self.assertFalse(IPublishInfo(article).published)


class TestProcess(zeit.newsimport.testing.FunctionalTestCase):
    def test_import_new_article(self):
        entry = self.dpa.get_entries()[0]
        zeit.newsimport.news.process_task(entry)
        article = ICMSContent(self.layer['dpa_article_id'])
        transaction.commit()
        self.assertTrue(IPublishInfo(article).published)
        self.assertEqual(1, self.layer['dpa_mock'].delete_entry.call_count)

    def test_article_containing_only_image_is_ignored(self):
        """
        Meaning, an image, without additional content like article body
        or headline
        """
        entry = self.dpa.get_entries()[3]
        zeit.newsimport.news.process_task(entry)
        article = ICMSContent('http://xml.zeit.de/news/2022-02/23/energiekosten', None)
        self.assertEqual(None, article)

    def test_update_older_article(self):
        entry = self.dpa.get_entries()[0]
        # NOTE article has to be created first
        zeit.newsimport.news.process_task(entry)
        transaction.commit()

        self.connector.search_result = [self.layer['dpa_article_id']]
        entry['headline'] = 'Updated headline'
        entry['version'] = 7
        with mock.patch(FIND_IMAGE) as find_img:
            find_img.return_value = ICMSContent(self.layer['dpa_article_id'] + '-image-group/')
            zeit.newsimport.news.process_task(entry)
            transaction.commit()
        article = ICMSContent(self.layer['dpa_article_id'])
        self.assertTrue(IPublishInfo(article).published)
        self.assertEqual('Updated headline', article.title)
        self.assertEqual(2, self.layer['dpa_mock'].delete_entry.call_count)

    def test_retract_article(self):
        entry = self.dpa.get_entries()[0]
        # NOTE article has to be created first
        zeit.newsimport.news.process_task(entry)
        transaction.commit()

        self.connector.search_result = [self.layer['dpa_article_id']]
        entry['pubstatus'] = 'canceled'
        zeit.newsimport.news.process_task(entry)
        transaction.commit()
        article = ICMSContent(self.layer['dpa_article_id'], None)
        self.assertEqual(None, article)
        self.assertEqual(2, self.layer['dpa_mock'].delete_entry.call_count)
        # should throw no errors if retract already happened
        with mock.patch('zeit.workflow.publish.Publish.retract') as retract:
            zeit.newsimport.news.process_task(entry)
            self.assertFalse(retract.called)
        transaction.commit()
        self.assertEqual(3, self.layer['dpa_mock'].delete_entry.call_count)

    def test_delete_entry_if_entry_causes_no_updates(self):
        entry = self.dpa.get_entries()[0]
        # NOTE article has to be created first
        zeit.newsimport.news.process_task(entry)
        transaction.commit()

        self.connector.search_result = [self.layer['dpa_article_id']]
        zeit.newsimport.news.process_task(entry)
        transaction.commit()
        self.assertEqual(2, self.layer['dpa_mock'].delete_entry.call_count)

    def test_update_image_with_image_only_entry(self):
        article = self.add_article_with_image()
        article_version = zeit.newsimport.interfaces.IDPANews(article).version
        old_image_version = zeit.newsimport.interfaces.IDPANews(article.main_image.target).version
        self.assertTrue(article.main_image)
        self.assertEqual(3, old_image_version)

        entry = self.dpa.get_entries()[-1]
        entry['article_html'] = None
        entry['urn'] = entry['associations'][0]['urn']
        entry['version'] = 4
        entry['version_created'] = '2022-02-03T10:45:31+01:00'  # +1 day
        entry['associations'][0]['version'] = 4
        entry['associations'][0]['version_created'] = '2022-02-03T10:45:31+01:00'  # +1 day
        with mock.patch('zeit.newsimport.news.Entry.find_existing_content') as fi:
            fi.return_value = ICMSContent(f'{NEWS_ARTICLE_UNIQUEID}-image-group/')
            zeit.newsimport.news.process_task(entry)
            transaction.commit()

        article = zeit.cms.interfaces.ICMSContent(NEWS_ARTICLE_UNIQUEID)
        self.assertEqual(2, article_version)
        self.assertGreater(
            zeit.newsimport.interfaces.IDPANews(article.main_image.target).version,
            old_image_version,
        )
        self.assertEqual(1, self.layer['dpa_mock'].delete_entry.call_count)

    def test_exception_is_no_reraised(self):
        entry = self.dpa.get_entries()[0]
        with mock.patch('zeit.newsimport.news.Entry.find_existing_content') as fi:
            fi.side_effect = Exception('Provoked')
            zeit.newsimport.news.process_task(entry)
            transaction.commit()

        self.assertEqual(0, self.layer['dpa_mock'].delete_entry.call_count)


class DPATOTMSTest(zeit.newsimport.testing.FunctionalTestCase):
    layer = zeit.newsimport.testing.CELERY_LAYER

    @pytest.fixture(autouse=True)
    def _caplog(self, caplog):
        self.caplog = caplog

    def tearDown(self):
        self.layer['tms'].generate_keyword_list.return_value = mock.DEFAULT
        super().tearDown()

    def test_article_should_send_keywords_to_tms_before_publish(self):
        tms = self.layer['tms']
        zope.component.getGlobalSiteManager().registerUtility(tms, ITMS)
        tms.generate_keyword_list.return_value = [
            zeit.cms.tagging.tag.Tag(label='one', entity_type='keyword'),
            zeit.cms.tagging.tag.Tag(label='two', entity_type='keyword'),
        ]

        entry = self.dpa.get_entries()[0]
        zeit.newsimport.news.process_task(entry)
        transaction.commit()
        zeit.workflow.testing.run_tasks()

        uniqueid = 'http://xml.zeit.de/news/2021-12/15/beispielmeldung-ueberschrift'

        log_publish = f'Publishing {uniqueid}'
        log_tags = f'Updating tags for {uniqueid}'

        index_tags, index_publish = None, None
        for i, record in enumerate(self.caplog.records):
            if record.message == log_publish:
                index_publish = i
            elif record.message == log_tags:
                index_tags = i

            if index_publish and index_tags:
                break

        self.assertGreater(index_publish, index_tags, 'Publish should happen after tags update')
        content = ICMSContent(uniqueid)
        self.assertTrue(isinstance(content, zeit.content.article.article.Article))
        self.assertTrue(IPublishInfo(content).published)
        self.assertEqual(['one', 'two'], [x.label for x in content.keywords])
