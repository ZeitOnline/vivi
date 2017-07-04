from datetime import datetime
from zeit.brightcove.convert2 import Video as BCVideo
from zeit.content.video.video import Video as CMSVideo
import mock
import pytz
import zeit.brightcove.testing
import zeit.cms.testing


class VideoTest(zeit.cms.testing.FunctionalTestCase,
                zeit.cms.tagging.testing.TaggingHelper):

    layer = zeit.brightcove.testing.ZCML_LAYER

    def test_converts_cms_fields_to_bc_names(self):
        cms = CMSVideo()
        cms.title = u'title'
        cms.teaserText = u'teaser'
        bc = BCVideo.from_cms(cms)
        self.assertEqual('title', bc.title)
        self.assertEqual('title', bc.data['name'])
        self.assertEqual('teaser', bc.teaserText)
        self.assertEqual('teaser', bc.data['description'])

    def test_setting_readonly_field_raises(self):
        bc = BCVideo()
        with self.assertRaises(AttributeError):
            bc.id = 'id'

    def test_missing_data_returns_field_default(self):
        bc = BCVideo()
        self.assertEqual(None, bc.ressort)

    def test_bc_names_with_slash_denote_nested_dict(self):
        cms = CMSVideo()
        cms.ressort = u'Deutschland'
        bc = BCVideo.from_cms(cms)
        self.assertEqual('Deutschland', bc.ressort)
        self.assertEqual('Deutschland', bc.data['custom_fields']['ressort'])

    def test_readonly_fields_are_removed_for_writing(self):
        bc = BCVideo()
        bc.data['id'] = 'foo'
        self.assertNotIn('id', bc.write_data)

    def test_looks_up_type_conversion_by_field(self):
        cms = CMSVideo()
        cms.commentsAllowed = True
        bc = BCVideo.from_cms(cms)
        self.assertEqual(True, bc.commentsAllowed)
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
        self.assertEqual(
            (self.repository['a1'], self.repository['a2']), bc.authorships)

    def test_converts_keywords(self):
        cms = CMSVideo()
        self.setup_tags('staatsanwaltschaft', 'parlament')
        bc = BCVideo.from_cms(cms)
        self.assertEqual(
            'staatsanwaltschaft;parlament',
            bc.data['custom_fields']['cmskeywords'])
        self.assertEqual(cms.keywords, bc.keywords)

    def test_converts_product(self):
        cms = CMSVideo()
        cms.product = zeit.cms.content.sources.PRODUCT_SOURCE(None).find(
            'TEST')
        bc = BCVideo.from_cms(cms)
        self.assertEqual('TEST', bc.data['custom_fields']['produkt-id'])
        self.assertEqual(cms.product, bc.product)

    def test_product_defaults_to_reuters(self):
        bc = BCVideo()
        bc.data['reference_id'] = '1234'
        self.assertEqual('Reuters', bc.product.id)

    def test_converts_serie(self):
        cms = CMSVideo()
        cms.serie = zeit.content.video.interfaces.IVideo['serie'].source(
            None).find('erde/umwelt')
        bc = BCVideo.from_cms(cms)
        self.assertEqual('erde/umwelt', bc.data['custom_fields']['serie'])
        self.assertEqual(cms.serie, bc.serie)

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
        self.assertEqual(related.related, bc.related)

    def test_converts_sources(self):
        bc = BCVideo()
        bc.data['sources'] = [{
            'asset_id': '83006421001',
            'codec': 'H264',
            'container': 'MP4',
            'duration': 85163,
            'encoding_rate': 1264000,
            'height': 720,
            'remote': False,
            'size': 13453446,
            'src': 'https://brightcove.hs.llnwd.net/e1/pd/...',
            'uploaded_at': '2010-05-05T08:26:48.704Z',
            'width': 1280,
        }]
        sources = bc.sources
        self.assertEqual(1, len(sources))
        src = sources[0]
        self.assertEqual(1280, src.frame_width)
        self.assertEqual('https://brightcove.hs.llnwd.net/e1/pd/...', src.url)
        self.assertEqual(85163, src.video_duration)

    def test_converts_timestamps(self):
        bc = BCVideo()
        bc.data['created_at'] = '2017-05-15T08:24:55.916Z'
        self.assertEqual(
            datetime(2017, 5, 15, 8, 24, 55, 916000, tzinfo=pytz.UTC),
            bc.date_created)

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
            'custom_fields': {
                'allow_comments': '1',
                'authors': 'http://xml.zeit.de/a1',
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
        self.assertEqual('myvid', cms.brightcove_id)
        self.assertEqual('title', cms.title)
        self.assertEqual(True, cms.commentsAllowed)
        self.assertEqual(['http://xml.zeit.de/a1'],
                         [x.target.uniqueId for x in cms.authorships])
        self.assertEqual(['testtag', 'testtag2'],
                         [x.code for x in cms.keywords])
        self.assertEqual('TEST', cms.product.id)
        self.assertEqual(
            (zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/online/2007/01/eta-zapatero'),),
            zeit.cms.related.interfaces.IRelatedContent(cms).related)
        self.assertEqual('erde/umwelt', cms.serie.serienname)
        self.assertEqual('http://example.com/thumbnail', cms.thumbnail)
        self.assertEqual('http://example.com/still', cms.video_still)
        self.assertEqual('http://example.com/rendition', cms.renditions[0].url)

    def test_creates_deleted_video_on_notfound(self):
        with mock.patch('zeit.brightcove.connection2.CMSAPI.get_video') as get:
            with mock.patch('zeit.brightcove.resolve.query_video_id') as query:
                get.return_value = None
                query.return_value = (
                    'http://xml.zeit.de/online/2007/01/Somalia')
                bc = BCVideo.find_by_id('nonexistent')
        self.assertIsInstance(bc, zeit.brightcove.convert2.DeletedVideo)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/Somalia', bc.uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/', bc.__parent__.uniqueId)
