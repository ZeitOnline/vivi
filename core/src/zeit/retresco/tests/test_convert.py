# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.retresco.testing import create_testcontent
import datetime
import gocept.testing.assertion
import mock
import pytz
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.tagging.testing
import zeit.content.image.interfaces
import zeit.content.volume.volume
import zeit.retresco.interfaces
import zeit.retresco.tag
import zeit.retresco.testing


class ConvertTest(zeit.retresco.testing.FunctionalTestCase,
                  gocept.testing.assertion.String):

    maxDiff = None

    def test_smoke_converts_lots_of_fields(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article) as co:
            co.breaking_news = True
            co.product = zeit.cms.content.sources.Product(u'KINZ')
            co.keywords = (
                zeit.retresco.tag.Tag('Code1', 'keyword'),
                zeit.retresco.tag.Tag('Code2', 'keyword'))
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')

        images = zeit.content.image.interfaces.IImages(article)
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image) as co:
            zeit.content.image.interfaces.IImageMetadata(
                co).expires = datetime.datetime(2007, 4, 1)
        images.image = zeit.cms.interfaces.ICMSContent(image.uniqueId)

        data = zeit.retresco.interfaces.ITMSRepresentation(article)()
        # Extract fields for which we cannot easily/sensibly use assertEqual().
        self.assertStartsWith('{urn:uuid:', data.pop('doc_id'))
        self.assertStartsWith('<body', data.pop('body'))
        self.assertIsInstance(
            data['payload'].pop('date_last_modified'), datetime.datetime)

        teaser = (
            u'Im Zuge des äthiopischen Vormarsches auf Mogadischu kriechen '
            u'in Somalia auch die alten Miliz-Chefs wieder hervor.')
        self.assertEqual({
            'author': u'Hans Meiser',
            'date': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.UTC),
            'doc_type': 'article',
            'rtr_events': [],
            'rtr_keywords': ['Code1', 'Code2'],
            'rtr_locations': [],
            'rtr_organisations': [],
            'rtr_persons': [],
            'rtr_products': [],
            'section': u'/International',
            'supertitle': u'Somalia',
            'teaser': teaser,
            'teaser_img_subline': None,
            'teaser_img_url': u'/2006/DSC00109_2.JPG',
            'title': u'Rückkehr der Warlords',
            'url': u'/online/2007/01/Somalia',

            'payload': {
                'access': u'free',
                'allow_comments': False,
                'article_genre': None,
                'article_header': u'default',
                'article_template': u'article',
                'authors': [],
                'author_names': [u'Hans Meiser'],
                'channels': [],
                'cms_icon': '/@@/zeit-content-article-interfaces-'
                            'IArticle-zmi_icon.png',
                'cms_preview_url': '',
                'date_first_released': None,
                'date_last_published': None,
                'date_last_published_semantic': None,
                'date_last_semantic_change': None,
                'date_print_published': None,
                'is_amp': False,
                'is_breaking': None,
                'is_instant_article': False,
                'keywords': [
                    {'label': 'Code1', 'entity_type': 'keyword',
                     'pinned': False},
                    {'label': 'Code2', 'entity_type': 'keyword',
                     'pinned': False}],
                'lead_candidate': True,
                'page': None,
                'print_ressort': None,
                'product_id': u'KINZ',
                'publish_status': 'not-published',
                'published': False,
                'ressort': u'International',
                'serie': u'-',
                'show_comments': False,
                'storystreams': [],
                'sub_ressort': None,
                'subtitle': teaser,
                'supertitle': u'Somalia',
                'teaser_image': u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                'teaser_image_fill_color': None,
                'teaser_supertitle': None,
                'teaser_text': teaser,
                'teaser_title': u'Rückkehr der Warlords',
                'title': u'Rückkehr der Warlords',
                'tldr_date': None,
                'volume': 1,
                'year': 2007,
            },
        }, data)

    def test_converts_channels_correctly(self):
        content = create_testcontent()
        content.channels = (('Mainchannel', None),)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['Mainchannel'], data['payload']['channels'])

    def test_converts_storystreams_correctly(self):
        content = create_testcontent()
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'storystreams'].value_type.source(None)
        content.storystreams = (source.find('test'),)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['http://xml.zeit.de/storystream'],
                         data['payload']['storystreams'])

    def test_synthesizes_tms_teaser_if_none_present(self):
        content = create_testcontent()
        content.teaserText = None
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual('title', data['teaser'])

    def test_converts_volumes(self):
        volume = zeit.content.volume.volume.Volume()
        volume.uniqueId = 'http://xml.zeit.de/volume'
        zeit.cms.content.interfaces.IUUID(volume).id = 'myid'
        volume.year = 2015
        volume.volume = 1
        published = datetime.datetime(2015, 1, 1, 0, 0, tzinfo=pytz.UTC)
        volume.date_digital_published = published
        data = zeit.retresco.interfaces.ITMSRepresentation(volume)()
        self.assertEqual(u'Teäser 01/2015', data['title'])
        self.assertEqual(u'Teäser 01/2015', data['teaser'])
        self.assertEqual(published, data['payload']['date_digital_published'])

    def test_does_not_index_volume_properties_for_articles(self):
        content = create_testcontent()
        content.year = 2006
        content.volume = 49
        content_teaser = 'content teaser'
        content.teaserText = content_teaser
        content.product = zeit.cms.content.sources.Product(u'ZEI')
        self.repository['content'] = content
        volume = zeit.content.volume.volume.Volume()
        volume.year = content.year
        volume.volume = content.volume
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        self.repository['2006']['49']['ausgabe'] = volume

        found = zeit.content.volume.interfaces.IVolume(content)
        self.assertEqual(found, volume)

        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(content_teaser, data['teaser'])
