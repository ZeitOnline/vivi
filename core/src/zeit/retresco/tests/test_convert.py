# coding: utf-8
from zeit.cms.checkout.helper import checked_out
from zeit.retresco.testing import create_testcontent
import datetime
import gocept.testing.assertion
import pytz
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.content.advertisement.advertisement
import zeit.content.author.author
import zeit.content.image.interfaces
import zeit.content.image.testing
import zeit.content.infobox.infobox
import zeit.content.portraitbox.portraitbox
import zeit.content.volume.volume
import zeit.retresco.interfaces
import zeit.retresco.tag
import zeit.retresco.testing
import zeit.seo.interfaces


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
        self.assert_editing_fields(data)
        self.assertStartsWith('<body', data.pop('body'))

        teaser = (
            u'Im Zuge des äthiopischen Vormarsches auf Mogadischu kriechen '
            u'in Somalia auch die alten Miliz-Chefs wieder hervor.')
        self.assertEqual({
            'author': u'Hans Meiser',
            'date': '1970-01-01T00:00:00Z',
            'doc_type': 'article',
            'payload': {
                'body': {
                    'byline': u'Von Jochen Stahnke',
                    'subtitle': teaser,
                    'supertitle': u'Somalia',
                    'title': u'Rückkehr der Warlords'
                },
                'document': {
                    'DailyNL': False,
                    'artbox_thema': False,
                    'author': ['Hans Meiser'],
                    'banner': True,
                    'banner_content': True,
                    'breaking_news': True,
                    'color_scheme': u'Redaktion',
                    'comments': False,
                    'comments_premoderate': False,
                    'copyrights': 'ZEIT online',
                    'countings': True,
                    'foldable': True,
                    'has_recensions': False,
                    'header_layout': u'default',
                    'hide_adblocker_notification': False,
                    'hide_ligatus_recommendations': False,
                    'imagecount': '0',
                    'in_rankings': 'yes',
                    'is_amp': False,
                    'is_content': 'yes',
                    'is_instant_article': False,
                    'last_modified_by': u'zope.user',
                    'lead_candidate': True,
                    'minimal_header': False,
                    'mostread': 'yes',
                    'new_comments': '1',
                    'overscrolling': True,
                    'pagelabel': 'Online',
                    'paragraphsperpage': '6',
                    'recent_comments_first': False,
                    'rebrush_website_content': False,
                    'ressort': u'International',
                    'revision': '11',
                    'serie': u'-',
                    'show_commentthread': False,
                    'supertitle': 'Spitzmarke hierher',
                    'template': u'article',
                    'text-length': 1036,
                    'title': u'R\xfcckkehr der Warlords',
                    'tldr_milestone': False,
                    'topic': 'Politik',
                    'volume': 1,
                    'year': 2007
                },
                'head': {
                    'authors': [],
                    'teaser_image': u'http://xml.zeit.de/2006/DSC00109_2.JPG',
                },
                'meta': {
                    'type': 'article',
                },
                'tagging': {},
                'teaser': {
                    'text': teaser,
                    'title': u'Rückkehr der Warlords'
                },
                'vivi': {
                    'cms_icon': '/@@/zeit-content-article-interfaces-IArticle'
                                '-zmi_icon.png',
                    'cms_preview_url': '',
                    'publish_status': 'not-published'
                },
                'workflow': {
                    'last-modified-by': 'hegenscheidt',
                    'product-id': u'KINZ',
                    'status': u'OK'
                }
            },
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
            'url': u'/online/2007/01/Somalia'
        }, data)

    def assert_editing_fields(self, data):
        self.assertStartsWith('{urn:uuid:', data.pop('doc_id'))
        self.assertStartsWith(
            '{urn:uuid:', data['payload']['document'].pop('uuid'))
        self.assertStartsWith(
            str(datetime.date.today().year),
            data['payload']['document'].pop('date_last_checkout'))
        self.assertStartsWith(
            str(datetime.date.today().year),
            data['payload']['document'].pop(
                'date-last-modified',
                # Only IXMLContent has this
                str(datetime.date.today().year)))
        self.assertStartsWith(
            '<pickle', data['payload']['meta'].pop('provides'))
        self.assertStartsWith(
            '<ns0:rankedTags', data['payload'].get('tagging', {}).pop(
                'keywords', '<ns0:rankedTags'))

    def test_converts_channels_correctly(self):
        content = create_testcontent()
        content.channels = (('Mainchannel', None),)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(
            ['Mainchannel'], data['payload']['document']['channels'])

    def test_converts_storystreams_correctly(self):
        content = create_testcontent()
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'storystreams'].value_type.source(None)
        content.storystreams = (source.find('test'),)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['test'],
                         data['payload']['document']['storystreams'])

    def test_synthesizes_tms_teaser_if_none_present(self):
        content = create_testcontent()
        content.teaserText = None
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual('title', data['teaser'])

    def test_converts_volume(self):
        volume = zeit.content.volume.volume.Volume()
        volume.uniqueId = 'http://xml.zeit.de/volume'
        zeit.cms.content.interfaces.IUUID(volume).id = 'myid'
        volume.year = 2015
        volume.volume = 1
        volume.product = zeit.cms.content.sources.Product(u'ZEI')
        volume.set_cover('ipad', 'ZEI', self.repository['testcontent'])
        published = datetime.datetime(2015, 1, 1, 0, 0, tzinfo=pytz.UTC)
        volume.date_digital_published = published
        data = zeit.retresco.interfaces.ITMSRepresentation(volume)()
        self.assertEqual(u'Teäser 01/2015', data['title'])
        self.assertEqual(u'Teäser 01/2015', data['teaser'])
        self.assertEqual(
            published.isoformat(),
            data['payload']['document']['date_digital_published'])
        self.assertEqual([{
            'id': 'ipad', 'product_id': 'ZEI',
            'href': 'http://xml.zeit.de/testcontent'}],
            data['payload']['head']['covers'])

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

    def test_drops_empty_properties(self):
        content = create_testcontent()
        props = zeit.connector.interfaces.IWebDAVProperties(content)
        props[('page', 'http://namespaces.zeit.de/CMS/document')] = None
        props[('reported_on', 'http://namespaces.zeit.de/CMS/vgwort')] = ''
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertNotIn('page', data['payload']['document'])
        self.assertNotIn('vgwort', data['payload'])

    def test_converts_image(self):
        image = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image):
            pass  # trigger uuid creation
        data = zeit.retresco.interfaces.ITMSRepresentation(image)()
        self.assert_editing_fields(data)
        self.assertEqual({
            'body': '<body/>',
            'date': '1970-01-01T00:00:00Z',
            'doc_type': 'image',
            'payload': {
                'document': {
                    'author': [u'Jochen Stahnke'],
                    'banner': True,
                    'last_modified_by': 'zope.user',
                },
                'meta': {'type': 'image'},
                'teaser': {
                    'title': 'DSC00109_2.JPG',
                    'text': 'DSC00109_2.JPG',
                },
                'vivi': {
                    'cms_icon': ('/@@/zeit-content-image-interfaces'
                                 '-IImage-zmi_icon.png'),
                    'cms_preview_url': ('/repository/2006/'
                                        'DSC00109_2.JPG/thumbnail'),
                    'publish_status': 'not-published'
                }
            },
            'url': '/2006/DSC00109_2.JPG',
            'title': 'DSC00109_2.JPG',
            'teaser': 'DSC00109_2.JPG',
        }, data)

    def test_converts_imagegroup(self):
        group = zeit.content.image.testing.create_image_group()
        with checked_out(group) as co:
            meta = zeit.content.image.interfaces.IImageMetadata(co)
            meta.title = u'mytitle'
            meta.caption = u'mycaption'
        data = zeit.retresco.interfaces.ITMSRepresentation(group)()
        self.assert_editing_fields(data)
        self.assertEqual({
            'body': '<body/>',
            'date': '1970-01-01T00:00:00Z',
            'doc_type': 'image-group',
            'payload': {
                'document': {
                    'last_modified_by': 'zope.user',
                    'title': 'mytitle',
                },
                'image': {'caption': 'mycaption'},
                'meta': {'type': 'image-group'},
                'teaser': {
                    'title': 'mytitle',
                    'text': 'mycaption',
                },
                'vivi': {
                    'cms_icon': ('/@@/zeit-content-image-interfaces'
                                 '-IImageGroup-zmi_icon.png'),
                    'cms_preview_url': '/repository/image-group/thumbnail',
                    'publish_status': 'not-published'
                }
            },
            'url': '/image-group/',
            'title': 'mytitle',
            'teaser': 'mycaption',
        }, data)

    def test_skips_newsimport_images(self):
        group = zeit.content.image.testing.create_image_group()
        with checked_out(group):
            pass  # trigger uuid creation
        self.repository['news'] = zeit.cms.repository.folder.Folder()
        self.repository['news']['group'] = group
        data = zeit.retresco.interfaces.ITMSRepresentation(group)()
        self.assertEqual(None, data)

    def test_converts_infobox(self):
        self.repository['infobox'] = zeit.content.infobox.infobox.Infobox()
        with checked_out(self.repository['infobox']) as co:
            co.supertitle = 'mytitle'
            co.contents = (('foo!', '<p>bar!</p>'),)
        data = zeit.retresco.interfaces.ITMSRepresentation(
            self.repository['infobox'])()
        self.assertEqual('infobox', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual({
            'supertitle': 'mytitle',
            'title': 'foo!',
            'text': '<p>bar!</p>\n',
        }, data['payload']['teaser'])

    def test_converts_portraitbox(self):
        self.repository[
            'portraitbox'] = zeit.content.portraitbox.portraitbox.Portraitbox()
        with checked_out(self.repository['portraitbox']) as co:
            co.name = 'mytitle'
            co.text = '<p>my text</p>'
        data = zeit.retresco.interfaces.ITMSRepresentation(
            self.repository['portraitbox'])()
        self.assertEqual('portraitbox', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual({
            'title': 'mytitle',
            'text': '<p>my text</p>',
        }, data['payload']['teaser'])

    def test_converts_author(self):
        self.repository['willy'] = zeit.content.author.author.Author()
        with checked_out(self.repository['willy']) as co:
            co.firstname = u'William'
            co.lastname = u'Shakespeare'
            co.summary = u'To be...'
            co.biography = '...or not to be!'
        data = zeit.retresco.interfaces.ITMSRepresentation(
            self.repository['willy'])()
        self.assertEqual('author', data['doc_type'])
        self.assertEqual('William Shakespeare', data['title'])
        self.assertEqual({
            'supertitle': 'To be...',
            'title': 'William Shakespeare',
            'text': '...or not to be!',
        }, data['payload']['teaser'])

    def test_converts_text(self):
        text = zeit.content.text.text.Text()
        text.text = ''
        self.repository['mytext'] = text
        data = zeit.retresco.interfaces.ITMSRepresentation(
            self.repository['mytext'])()
        self.assertEqual('text', data['doc_type'])
        self.assertEqual('mytext', data['title'])
        self.assertEqual({'title': 'mytext'}, data['payload']['teaser'])

    def test_converts_rawxml(self):
        self.repository['embed'] = zeit.content.rawxml.rawxml.RawXML()
        with checked_out(self.repository['embed']) as co:
            co.title = 'mytitle'
        data = zeit.retresco.interfaces.ITMSRepresentation(
            self.repository['embed'])()
        self.assertEqual('rawxml', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual({'title': 'embed'}, data['payload']['teaser'])

    def test_converts_advertistement(self):
        adv = zeit.content.advertisement.advertisement.Advertisement()
        adv.supertitle = 'super title!'
        adv.title = 'mytitle'
        adv.text = 'super text...'
        self.repository['adv'] = adv
        data = zeit.retresco.interfaces.ITMSRepresentation(
            self.repository['adv'])()
        self.assertEqual('advertisement', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual({
            'supertitle': 'super title!',
            'title': 'mytitle',
            'text': 'super text...',
        }, data['payload']['teaser'])

    def test_converts_seo_properties(self):
        content = create_testcontent()
        seo = zeit.seo.interfaces.ISEO(content)
        seo.meta_robots = 'noindex, follow,noarchive'
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(
            ['noindex', 'follow', 'noarchive'],
            data['payload']['seo']['robots'])

    def test_converts_push_config(self):
        content = create_testcontent()
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [
            {'type': 'facebook', 'account': 'fb-test', 'enabled': False},
            {'type': 'facebook', 'account': 'fb-magazin', 'enabled': False},
            {'type': 'mobile', 'payload_template': 'mytemplate.json',
             'enabled': True},
        ]
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual({
            'facebook': {'account': ['fb-test', 'fb-magazin']},
            'mobile': {'payload_template': ['mytemplate.json']},
        }, data['payload']['push'])
