# coding: utf-8
from unittest import mock

from pendulum import datetime
import pendulum
import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.content.dynamicfolder.testing import create_dynamic_folder
from zeit.retresco.testing import create_testcontent
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.tagging.tag
import zeit.content.advertisement.advertisement
import zeit.content.audio.audio
import zeit.content.audio.testing
import zeit.content.author.author
import zeit.content.gallery.gallery
import zeit.content.image.interfaces
import zeit.content.image.testing
import zeit.content.infobox.infobox
import zeit.content.portraitbox.portraitbox
import zeit.content.volume.volume
import zeit.retresco.interfaces
import zeit.retresco.testing
import zeit.seo.interfaces


class ConvertTest(zeit.retresco.testing.FunctionalTestCase):
    maxDiff = None

    def test_smoke_converts_lots_of_fields(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article) as co:
            co.breaking_news = True
            co.product = zeit.cms.content.sources.Product('KINZ')
            co.keywords = (
                zeit.cms.tagging.tag.Tag('Code1', 'keyword'),
                zeit.cms.tagging.tag.Tag('Code2', 'keyword'),
            )
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')

        images = zeit.content.image.interfaces.IImages(article)
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image) as co:
            zeit.content.image.interfaces.IImageMetadata(co).expires = datetime(2007, 4, 1)
        images.image = zeit.cms.interfaces.ICMSContent(image.uniqueId)

        data = zeit.retresco.interfaces.ITMSRepresentation(article)()
        # hint: attributes defined with use_default=True don't occur in data

        # Extract fields for which we cannot easily/sensibly use assertEqual().
        self.assert_editing_fields(data)
        self.assertStartsWith('<body', data.pop('body'))

        teaser = (
            'Im Zuge des äthiopischen Vormarsches auf Mogadischu kriechen '
            'in Somalia auch die alten Miliz-Chefs wieder hervor.'
        )
        self.assertEqual(
            {
                'date': '1970-01-01T00:00:00Z',
                'doc_type': 'article',
                'payload': {
                    'body': {
                        'subtitle': teaser,
                        'supertitle': 'Somalia',
                        'title': 'Rückkehr der Warlords',
                    },
                    'document': {
                        'artbox_thema': False,
                        'audio_speechbert': True,
                        'author': 'Hans Meiser',
                        'banner': True,
                        'banner_content': True,
                        'color_scheme': 'Redaktion',
                        'comments': False,
                        'comments_premoderate': False,
                        'copyrights': 'ZEIT online',
                        'has_recensions': False,
                        'header_layout': 'default',
                        'hide_adblocker_notification': False,
                        'hide_ligatus_recommendations': False,
                        'avoid_create_summary': False,
                        'imagecount': '0',
                        'in_rankings': 'yes',
                        'is_content': 'yes',
                        'last_modified_by': 'zope.user',
                        'mostread': 'yes',
                        'new_comments': '1',
                        'overscrolling': True,
                        'pagelabel': 'Online',
                        'paragraphsperpage': '6',
                        'prevent_ligatus_indexing': False,
                        'ressort': 'International',
                        'revision': '11',
                        'serie': '-',
                        'show_commentthread': False,
                        'supertitle': 'Spitzmarke hierher',
                        'template': 'article',
                        'text-length': 1036,
                        'title': 'R\xfcckkehr der Warlords',
                        'topic': 'Politik',
                        'volume': 1,
                        'year': 2007,
                    },
                    'head': {
                        'authors': [],
                        'audio_references': [],
                        'agencies': [],
                        'teaser_image': 'http://xml.zeit.de/2006/DSC00109_2.JPG',
                    },
                    'meta': {
                        'type': 'article',
                    },
                    'tagging': {},
                    'teaser': {'text': teaser, 'title': 'Rückkehr der Warlords'},
                    'vivi': {
                        'cms_icon': '/@@/zeit-content-article-interfaces-IArticle' '-zmi_icon.png',
                        'publish_status': 'not-published',
                    },
                    'workflow': {
                        'last-modified-by': 'hegenscheidt',
                        'product-id': 'KINZ',
                        'status': 'OK',
                    },
                },
                'rtr_events': [],
                'rtr_keywords': ['Code1', 'Code2'],
                'rtr_locations': [],
                'rtr_organisations': [],
                'rtr_persons': [],
                'rtr_products': [],
                'section': '/International',
                'supertitle': 'Somalia',
                'teaser': teaser,
                'teaser_img_url': '/2006/DSC00109_2.JPG',
                'title': 'Rückkehr der Warlords',
                'url': '/online/2007/01/Somalia',
            },
            data,
        )

    def assert_editing_fields(self, data):
        self.assertStartsWith('{urn:uuid:', data.pop('doc_id'))
        self.assertStartsWith('{urn:uuid:', data['payload']['document'].pop('uuid'))
        self.assertStartsWith(
            str(pendulum.today().year), data['payload']['document'].pop('date_last_checkout')
        )
        self.assertStartsWith(
            str(pendulum.today().year), data['payload']['meta'].pop('tms_last_indexed')
        )
        self.assertStartsWith(
            str(pendulum.today().year),
            data['payload']['document'].pop('date_last_modified', str(pendulum.today().year)),
        )
        self.assertStartsWith('<pickle', data['payload']['meta'].pop('provides'))
        self.assertStartsWith(
            '<ns0:rankedTags', data['payload'].get('tagging', {}).pop('keywords', '<ns0:rankedTags')
        )

    def test_converts_channels_correctly(self):
        content = create_testcontent()
        content.channels = (('Mainchannel', None),)
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['Mainchannel'], data['payload']['document']['channels'])

    def test_converts_authorships(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        self.repository['author'] = author
        content = create_testcontent()
        content.authorships = [content.authorships.create(self.repository['author'])]
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['http://xml.zeit.de/author'], data['payload']['head']['authors'])

    def test_converts_agencies(self):
        author = zeit.content.author.author.Author()
        author.firstname = 'William'
        author.lastname = 'Shakespeare'
        self.repository['author'] = author
        content = create_testcontent()
        content.agencies = [self.repository['author']]
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['http://xml.zeit.de/author'], data['payload']['head']['agencies'])

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
        volume.product = zeit.cms.content.sources.Product('ZEI')
        volume.set_cover('ipad', 'ZEI', self.repository['testcontent'])
        published = datetime(2015, 1, 1, 0, 0)
        volume.date_digital_published = published
        data = zeit.retresco.interfaces.ITMSRepresentation(volume)()
        self.assertEqual('Teäser 01/2015', data['title'])
        self.assertEqual('Teäser 01/2015', data['teaser'])
        self.assertEqual(
            published.isoformat(), data['payload']['document']['date_digital_published']
        )
        self.assertEqual(
            [{'id': 'ipad', 'product_id': 'ZEI', 'href': 'http://xml.zeit.de/testcontent'}],
            data['payload']['head']['covers'],
        )

    def test_does_not_index_volume_properties_for_articles(self):
        content = create_testcontent()
        content.year = 2006
        content.volume = 49
        content_teaser = 'content teaser'
        content.teaserText = content_teaser
        content.product = zeit.cms.content.sources.Product('ZEI')
        self.repository['content'] = content
        volume = zeit.content.volume.volume.Volume()
        volume.year = content.year
        volume.volume = content.volume
        volume.product = zeit.cms.content.sources.Product('ZEI')
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

    def test_drops_deprecated_properties(self):
        content = create_testcontent()
        props = zeit.connector.interfaces.IWebDAVProperties(content)
        props[('countings', 'http://namespaces.zeit.de/CMS/document')] = 'yes'
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertNotIn('countings', data['payload']['document'])

    def test_converts_image(self):
        image = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with checked_out(image):
            pass  # satisfy editing fields
        data = zeit.retresco.interfaces.ITMSRepresentation(image)()
        self.assert_editing_fields(data)
        self.assertEqual(
            {
                'body': '<body/>',
                'date': '1970-01-01T00:00:00Z',
                'doc_type': 'image',
                'payload': {
                    'document': {
                        'author': 'Jochen Stahnke',
                        'banner': True,
                        'last_modified_by': 'zope.user',
                    },
                    'meta': {'type': 'image'},
                    'body': {
                        'title': 'DSC00109_2.JPG',
                        'text': 'DSC00109_2.JPG',
                    },
                    'tagging': {},
                    'vivi': {
                        'cms_icon': ('/@@/zeit-content-image-interfaces' '-IImage-zmi_icon.png'),
                        'cms_preview_url': ('/repository/2006/' 'DSC00109_2.JPG/thumbnail'),
                        'publish_status': 'not-published',
                    },
                },
                'url': '/2006/DSC00109_2.JPG',
                'title': 'DSC00109_2.JPG',
                'teaser': 'DSC00109_2.JPG',
            },
            data,
        )

    def test_converts_recipe_attributes(self):
        recipe = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/zeit-magazin/wochenmarkt/rezept'
        )
        with checked_out(recipe):
            pass
        data = zeit.retresco.interfaces.ITMSRepresentation(recipe)()
        payload = {
            'search': [
                'Die leckere Fleisch-Kombi:subheading',
                'Grillwurst:ingredient',
                'Hahn:ingredient',
                'Hähnchen:ingredient',
                'Hühnchen:ingredient',
                'Pastagerichte:category',
                'Tomate:ingredient',
                'Tomaten-Grieß:recipe_title',
                'Tomaten:ingredient',
                'Vier Rezepte für eine Herdplatte:title',
                'Wurst-Hähnchen:recipe_title',
                'Wurst:ingredient',
                'Wurstiges:category',
            ],
            'subheadings': ['Die leckere Fleisch-Kombi'],
            'titles': ['Tomaten-Grieß', 'Wurst-Hähnchen'],
            'categories': ['pastagerichte', 'wurstiges'],
            'complexities': ['ambitioniert', 'einfach'],
            'servings': ['2', '6'],
            'times': ['unter 30 Minuten', 'über 60 Minuten'],
            'ingredients': [
                'brathaehnchen',
                'bratwurst',
                'chicken-nuggets',
                'gries',
                'gurke',
                'tomate',
            ],
        }
        self.assertEqual(payload, data['payload']['recipe'])

    def test_converts_imagegroup(self):
        group = zeit.content.image.testing.create_image_group()
        with checked_out(group) as co:
            meta = zeit.content.image.interfaces.IImageMetadata(co)
            meta.title = 'mytitle'
            meta.caption = 'mycaption'
        data = zeit.retresco.interfaces.ITMSRepresentation(group)()
        self.assert_editing_fields(data)
        self.assertEqual(
            {
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
                    'body': {
                        'title': 'mytitle',
                        'text': 'mycaption',
                    },
                    'tagging': {},
                    'vivi': {
                        'cms_icon': (
                            '/@@/zeit-content-image-interfaces' '-IImageGroup-zmi_icon.png'
                        ),
                        'cms_preview_url': '/repository/image-group/thumbnail',
                        'publish_status': 'not-published',
                    },
                },
                'url': '/image-group/',
                'title': 'mytitle',
                'teaser': 'mycaption',
            },
            data,
        )

    def test_skips_newsimport_images(self):
        group = zeit.content.image.testing.create_image_group()
        self.repository['news'] = zeit.cms.repository.folder.Folder()
        self.repository['news']['group'] = group
        data = zeit.retresco.interfaces.ITMSRepresentation(group)()
        self.assertEqual(None, data)

    def test_converts_infobox(self):
        self.repository['infobox'] = zeit.content.infobox.infobox.Infobox()
        with checked_out(self.repository['infobox']) as co:
            co.supertitle = 'mytitle'
            co.contents = (('foo!', '<p>bar!</p>'),)
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['infobox'])()
        self.assertEqual('infobox', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual('mytitle', data['payload']['body']['supertitle'])
        self.assertEqual('foo!', data['payload']['body']['title'])
        self.assertEqual('<p>bar!</p>', data['payload']['body']['text'].strip())

    def test_converts_portraitbox(self):
        self.repository['portraitbox'] = zeit.content.portraitbox.portraitbox.Portraitbox()
        with checked_out(self.repository['portraitbox']) as co:
            co.name = 'mytitle'
            co.text = '<p>bar!</p>'
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['portraitbox'])()
        self.assertEqual('portraitbox', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual('mytitle', data['payload']['body']['title'])
        self.assertEqual('<p>bar!</p>', data['payload']['body']['text'].strip())

    def test_converts_author(self):
        self.repository['willy'] = zeit.content.author.author.Author()
        with checked_out(self.repository['willy']) as co:
            co.firstname = 'William'
            co.lastname = 'Shakespeare'
            co.summary = 'To be...'
            co.biography = '...or not to be!'
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['willy'])()
        self.assertEqual('author', data['doc_type'])
        self.assertEqual('William Shakespeare', data['title'])
        self.assertEqual(
            {
                'supertitle': 'To be...',
                'title': 'William Shakespeare',
                'text': '...or not to be!',
            },
            data['payload']['body'],
        )

    def test_converts_text(self):
        text = zeit.content.text.text.Text()
        text.text = ''
        self.repository['mytext'] = text
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['mytext'])()
        self.assertEqual('text', data['doc_type'])
        self.assertEqual('mytext', data['title'])
        self.assertEqual({'title': 'mytext'}, data['payload']['body'])

    def test_converts_rawxml(self):
        self.repository['embed'] = zeit.content.rawxml.rawxml.RawXML()
        with checked_out(self.repository['embed']) as co:
            co.title = 'mytitle'
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['embed'])()
        self.assertEqual('rawxml', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual({'title': 'embed'}, data['payload']['body'])

    def test_converts_advertistement(self):
        adv = zeit.content.advertisement.advertisement.Advertisement()
        adv.supertitle = 'super title!'
        adv.title = 'mytitle'
        adv.text = 'super text...'
        self.repository['adv'] = adv
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['adv'])()
        self.assertEqual('advertisement', data['doc_type'])
        self.assertEqual('mytitle', data['title'])
        self.assertEqual(
            {
                'supertitle': 'super title!',
                'title': 'mytitle',
                'text': 'super text...',
            },
            data['payload']['body'],
        )

    def test_converts_seo_properties(self):
        content = create_testcontent()
        seo = zeit.seo.interfaces.ISEO(content)
        seo.meta_robots = 'noindex, follow,noarchive'
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(['noindex', 'follow', 'noarchive'], data['payload']['seo']['robots'])

    def test_converts_push_config(self):
        content = create_testcontent()
        push = zeit.push.interfaces.IPushMessages(content)
        push.message_config = [
            {'type': 'facebook', 'account': 'fb-test', 'enabled': False},
            {'type': 'facebook', 'account': 'fb-magazin', 'enabled': False},
            {
                'type': 'mobile',
                'payload_template': 'mytemplate.json',
                'enabled': True,
                'uses_image': 1,
            },
        ]
        data = zeit.retresco.interfaces.ITMSRepresentation(content)()
        self.assertEqual(
            {
                'facebook': {'account': ['fb-test', 'fb-magazin']},
                'mobile': {'payload_template': ['mytemplate.json'], 'uses_image': [True]},
            },
            data['payload']['push'],
        )

    def test_converts_gallery_count(self):
        gallery = zeit.content.gallery.gallery.Gallery()
        gallery.title = 'title'
        gallery.teaserText = 'teaser'
        gallery.image_folder = self.repository['2006']
        self.repository['gallery'] = gallery
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['gallery'])()
        self.assertEqual(2, data['payload']['head']['visible_entry_count'])
        content = zeit.retresco.interfaces.ITMSContent(data)
        self.assertEqual(2, zeit.content.gallery.interfaces.IVisibleEntryCount(content))

    def test_converts_dynamicfolder(self):
        folder = create_dynamic_folder(
            'zeit.content.dynamicfolder:tests/fixtures/dynamic-centerpages/',
            files=['config.xml', 'tags.xml', 'template.xml'],
        )
        self.repository['dynamic'] = folder
        data = zeit.retresco.interfaces.ITMSRepresentation(self.repository['dynamic'])()
        self.assertEqual(
            'http://xml.zeit.de/data/config.xml', data['payload']['document']['config_file']
        )

    def test_converts_article_with_audio(self):
        audio = zeit.content.audio.testing.AudioBuilder().build(self.repository)
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        with checked_out(article) as co:
            audios = zeit.content.audio.interfaces.IAudioReferences
            audios(co).items = (self.repository['audio'],)
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        data = zeit.retresco.interfaces.ITMSRepresentation(article)()
        assert data['payload']['head']['audio_references'] == [audio.uniqueId]


class ConvertWithScalarTypesTest(zeit.retresco.testing.FunctionalTestCase):
    def test_smoke_converts_lots_of_fields(self):
        FEATURE_TOGGLES.set('write_metadata_columns')
        FEATURE_TOGGLES.set('read_metadata_columns')
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        # add some timestamps
        with checked_out(article):
            pass
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with mock.patch.object(tms, '_request') as request:
            tms.enrich(article)
            payload = request.call_args[1]['json']['payload']
            assert isinstance(payload['document']['date_last_checkout'], str)
