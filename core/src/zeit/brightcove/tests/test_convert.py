from datetime import datetime
from zeit.brightcove.convert import Video as BCVideo
from zeit.content.video.video import Video as CMSVideo
import mock
import pytz
import zeit.brightcove.testing
import zeit.cms.testing
import zeit.content.video.playlist


class VideoTest(zeit.cms.testing.FunctionalTestCase,
                zeit.cms.tagging.testing.TaggingHelper):

    layer = zeit.brightcove.testing.LAYER

    def test_converts_cms_fields_to_bc_names(self):
        cms = CMSVideo()
        cms.title = u'title'
        cms.teaserText = u'teaser'
        bc = BCVideo.from_cms(cms)
        self.assertEqual('title', bc.data['name'])
        self.assertEqual('teaser', bc.data['description'])

    def test_readonly_fields_are_removed_for_writing(self):
        bc = BCVideo()
        bc.data['id'] = 'foo'
        self.assertNotIn('id', bc.write_data)

    def test_looks_up_type_conversion_by_field(self):
        cms = CMSVideo()
        cms.commentsAllowed = True
        bc = BCVideo.from_cms(cms)
        self.assertEqual('1', bc.data['custom_fields']['allow_comments'])

    def test_looks_up_folder_from_product_config(self):
        bc = BCVideo()
        bc.data['id'] = 'myvid'
        bc.data['created_at'] = '2017-05-15T08:24:55.916Z'
        self.assertEqual('http://xml.zeit.de/video/2017-05/myvid', bc.uniqueId)
        self.assertEqual(zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/video/2017-05/'), bc.__parent__)

    def test_converts_authors(self):
        from zeit.content.author.author import Author
        self.repository['a1'] = Author()
        self.repository['a2'] = Author()

        cms = CMSVideo()
        cms.authorships = (
            cms.authorships.create(self.repository['a1']),
            cms.authorships.create(self.repository['a2'])
        )
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'http://xml.zeit.de/a1 http://xml.zeit.de/a2',
            bc.data['custom_fields']['authors'])

    def test_converts_keywords(self):
        cms = CMSVideo()
        self.setup_tags('staatsanwaltschaft', 'parlament')
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'staatsanwaltschaft;parlament',
            bc.data['custom_fields']['cmskeywords'])

    def test_converts_product(self):
        cms = CMSVideo()
        cms.product = zeit.cms.content.sources.PRODUCT_SOURCE(None).find(
            'TEST')
        bc = BCVideo.from_cms(cms)
        self.assertEqual('TEST', bc.data['custom_fields']['produkt-id'])

    def test_product_defaults_to_reuters(self):
        bc = BCVideo()
        bc.data['reference_id'] = '1234'
        cms = CMSVideo()
        bc.apply_to_cms(cms)
        self.assertEqual('Reuters', cms.product.id)

    def test_converts_serie(self):
        cms = CMSVideo()
        cms.serie = zeit.content.video.interfaces.IVideo['serie'].source(
            None).find('erde/umwelt')
        bc = BCVideo.from_cms(cms)
        self.assertEqual('erde/umwelt', bc.data['custom_fields']['serie'])

    def test_converts_channels(self):
        cms = CMSVideo()
        cms.channels = (('Deutschland', 'Meinung'), ('International', None))
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'Deutschland Meinung;International',
            bc.data['custom_fields']['channels'])

    def test_converts_related(self):
        cms = CMSVideo()
        related = zeit.cms.related.interfaces.IRelatedContent(cms)
        related.related = (
            zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/online/2007/01/eta-zapatero'),)
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/eta-zapatero',
            bc.data['custom_fields']['ref_link1'])

    def test_converts_advertisement(self):
        cms = CMSVideo()
        cms.has_advertisement = False
        bc = BCVideo.from_cms(cms)
        self.assertEqual('FREE', bc.data['economics'])

    def test_converts_timestamps(self):
        bc = BCVideo()
        bc.data['created_at'] = '2017-05-15T08:24:55.916Z'
        self.assertEqual(
            datetime(2017, 5, 15, 8, 24, 55, 916000, tzinfo=pytz.UTC),
            bc.date_created)

    def test_only_strings_in_custom_fields(self):
        from zeit.content.author.author import Author
        self.repository['a1'] = Author()
        cms = CMSVideo()
        cms.authorships = (cms.authorships.create(self.repository['a1']),)
        cms.product = zeit.cms.content.sources.PRODUCT_SOURCE(None).find(
            'TEST')
        bc = BCVideo.from_cms(cms)
        for key, value in bc.data['custom_fields'].items():
            self.assertIsInstance(
                value, basestring, '%s should be a string' % key)

    def test_applies_values_to_cms_object(self):
        from zeit.content.author.author import Author
        self.repository['a1'] = Author()
        cms = CMSVideo()
        bc = BCVideo()
        bc.data = {
            'id': 'myvid',
            'name': 'title',
            'created_at': '2017-05-15T08:24:55.916Z',
            'state': 'ACTIVE',
            'economics': 'AD_SUPPORTED',
            'custom_fields': {
                'allow_comments': '1',
                'authors': 'http://xml.zeit.de/a1',
                'channels': 'Deutschland Meinung;International',
                'cmskeywords': 'testtag;testtag2',
                'produkt-id': 'TEST',
                'ref_link1': 'http://xml.zeit.de/online/2007/01/eta-zapatero',
                'serie': 'erde/umwelt',
            },
            'images': {
                'thumbnail': {'src': 'http://example.com/thumbnail'},
                'poster': {'src': 'http://example.com/still'},
            },
            'sources': [{
                'src': 'http://example.com/rendition',
            }],
        }
        bc.apply_to_cms(cms)
        self.assertEqual('myvid', cms.external_id)
        self.assertEqual('title', cms.title)
        self.assertEqual(True, cms.commentsAllowed)
        self.assertEqual(['http://xml.zeit.de/a1'],
                         [x.target.uniqueId for x in cms.authorships])
        self.assertEqual(['testtag', 'testtag2'],
                         [x.code for x in cms.keywords])
        self.assertEqual((('Deutschland', 'Meinung'), ('International', None)),
                         cms.channels)
        self.assertEqual('TEST', cms.product.id)
        self.assertEqual(True, cms.has_advertisement)
        self.assertEqual(
            (zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/online/2007/01/eta-zapatero'),),
            zeit.cms.related.interfaces.IRelatedContent(cms).related)
        self.assertEqual('erde/umwelt', cms.serie.serienname)

    def test_creates_deleted_video_on_notfound(self):
        with mock.patch('zeit.brightcove.connection.CMSAPI.get_video') as get:
            with mock.patch('zeit.brightcove.resolve.query_video_id') as query:
                get.return_value = None
                query.return_value = (
                    'http://xml.zeit.de/online/2007/01/Somalia')
                bc = BCVideo.find_by_id('nonexistent')
        self.assertIsInstance(bc, zeit.brightcove.convert.DeletedVideo)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/Somalia', bc.uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/', bc.__parent__.uniqueId)

    def test_missing_values_use_field_default(self):
        bc = BCVideo()
        cms = CMSVideo()
        bc.apply_to_cms(cms)
        self.assertTrue(cms.commentsAllowed)


class PlaylistTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.brightcove.testing.LAYER

    def test_converts_video_list(self):
        bc = zeit.brightcove.convert.Playlist()
        bc.data['video_ids'] = ['search-must-be-mocked']
        playlist = zeit.content.video.playlist.Playlist()
        with mock.patch('zeit.brightcove.resolve.query_video_id') as query:
            query.return_value = 'http://xml.zeit.de/online/2007/01/Somalia'
            bc.apply_to_cms(playlist)
            self.assertEqual(['http://xml.zeit.de/online/2007/01/Somalia'],
                             [x.uniqueId for x in playlist.videos])
