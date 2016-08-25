# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.retresco.testing import create_testcontent
import datetime
import gocept.testing.assertion
import mock
import pytz
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.tagging.testing
import zeit.cms.testing
import zeit.content.image.interfaces
import zeit.retresco.interfaces
import zeit.retresco.testing


class ConvertTest(zeit.cms.testing.FunctionalTestCase,
                  gocept.testing.assertion.String):

    layer = zeit.retresco.testing.ZCML_LAYER
    maxDiff = None

    def setUp(self):
        super(ConvertTest, self).setUp()
        self.patcher = mock.patch('zeit.cms.tagging.interfaces.ITagger')
        tagger = self.patcher.start()
        self.tags = zeit.cms.tagging.testing.FakeTags()
        tagger.return_value = self.tags

    def tearDown(self):
        self.patcher.stop()
        super(ConvertTest, self).tearDown()

    def test_smoke_converts_lots_of_fields(self):
        article = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article) as co:
            co.breaking_news = True
            co.title = "Strip <em>the</em> &amp; please"
            co.product = zeit.cms.content.sources.Product(u'KINZ')
        self.tags['Code1'] = zeit.cms.tagging.tag.Tag(
            'Code1', 'Code1', entity_type='keyword')
        self.tags['Code2'] = zeit.cms.tagging.tag.Tag(
            'Code2', 'Code2', entity_type='keyword')

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
            'section': u'International',
            'supertitle': u'Somalia',
            'startdate': datetime.datetime(9999, 1, 1, 0, 0, tzinfo=pytz.UTC),
            'teaser': teaser,
            'teaser_img_subline': None,
            'teaser_img_url': u'/2006/DSC00109_2.JPG',
            'title': u'Rückkehr der Warlords',
            'url': u'/online/2007/01/Somalia',

            'payload': {
                'acquisition': u'free',
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
                'lead_candidate': True,
                'page': None,
                'print_ressort': None,
                'product_id': u'KINZ',
                'publish_status': 'not-published',
                'published': False,
                'push_news': False,
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

    def test_not_published_transmits_future_startdate(self):
        content = create_testcontent()
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(9999, data['startdate'].year)
