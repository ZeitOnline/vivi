import lxml.objectify
import unittest
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.content.video.testing


class TestVideo(zeit.content.video.testing.TestCase):

    def test_videos_should_contain_subtitle_node_in_xml_even_if_none(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.subtitle = None  # set explicitly
        video = factory.next()  # in repository
        self.assertIn(
            'subtitle',
            [x.tag for x in video.xml.body.getchildren()])

    def test_security_should_allow_access_to_id_prefix(self):
        import zeit.cms.testing
        import zope.security.management
        from zope.security.proxy import ProxyFactory
        factory = zeit.content.video.testing.video_factory(self)
        factory.next()
        video = factory.next()  # in repository
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.mgr'):
            proxied = ProxyFactory(video)
            self.assertEqual('vid', proxied.id_prefix)

    def test_videos_use_their_own_serie_source(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.serie = zeit.cms.content.sources.Serie('VIDEO')
        video = factory.next()  # in repository
        self.assertEqual('VIDEO', video.serie.serienname)


class TestReference(zeit.content.video.testing.TestCase):

    def setUp(self):
        super(TestReference, self).setUp()
        self.node = lxml.objectify.XML(
            '<block xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:py="http://codespeak.net/lxml/objectify/pytype"/>')

    def create_video(self, **kw):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        for key, value in kw.items():
            setattr(video, key, value)
        video = factory.next()  # video is now in repository['video']

    def update(self, node):
        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(
            self.repository['video'])
        updater.update(node)

    def test_still_should_be_contained_in_xml_reference(self):
        self.create_video(video_still='http://stillurl')
        self.update(self.node)
        self.assertEqual(
            'http://stillurl', self.node['video-still'].get('src'))

    def test_thumbnail_should_be_contained_in_xml_reference(self):
        self.create_video(thumbnail='http://thumbnailurl')
        self.update(self.node)
        self.assertEqual(
            'http://thumbnailurl', self.node['thumbnail'].get('src'))

    def test_nodes_should_be_removed_from_reference(self):
        self.create_video(
            video_still='http://stillurl', thumbnail='http://thumbnailurl')
        self.update(self.node)
        with zeit.cms.checkout.helper.checked_out(
                self.repository['video']) as co:
            co.video_still = None
            co.thumbnail = None
        self.update(self.node)
        self.assertRaises(AttributeError, lambda: self.node['video-still'])
        self.assertRaises(AttributeError, lambda: self.node['thumbnail'])


class TestRenditionsProperty(unittest.TestCase):

    def test_element_factory_should_return_rendition(self):
        import mock
        from zeit.content.video.video import RenditionsProperty
        prop = RenditionsProperty(".foo")

        node = lxml.objectify.XML(
            "<rendition url='foo' frame_width='100' video_duration='93000'/>")
        rendition = prop._element_factory(node, mock.sentinel.tree)
        self.assertEqual(node.get('url'), rendition.url)
        self.assertEqual(int(node.get('frame_width')), rendition.frame_width)
        self.assertEqual(
            int(node.get('video_duration')), rendition.video_duration)

    def test_node_factory_should_return_node(self):
        from zeit.content.video.video import RenditionsProperty
        import mock
        prop = RenditionsProperty(".foo")
        rendition = mock.Mock()
        rendition.url = 'foo'
        rendition.frame_width = 100
        rendition.video_duration = 920
        node = prop._node_factory(rendition, mock.sentinel.tree)
        self.assertEqual('rendition', node.tag)
        self.assertEqual('foo', node.get('url'))
        self.assertEqual(100, int(node.get('frame_width')))
        self.assertEqual(920, int(node.get('video_duration')))

    def test_video_should_store_renditions(self):
        from zeit.content.video.video import Video
        from zeit.content.video.video import VideoRendition

        video = Video()
        rendition = VideoRendition()
        rendition.url = 'foo'
        rendition.frame_width = 100
        rendition.video_duration = 910
        rendition2 = VideoRendition()
        rendition2.url = 'baa'
        rendition2.frame_width = 200
        rendition2.video_duration = 920
        video.renditions = (rendition, rendition2)

        xmlstr = lxml.etree.tostring(
            video.xml.head.renditions, pretty_print=True)
        self.assertEqual('<renditions xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <rendition url="foo" frame_width="100" video_duration="910"/>\n  <rendition url="baa" frame_width="200" video_duration="920"/>\n</renditions>\n', xmlstr)

    def test_video_should_load_renditions(self):
        from zeit.content.video.video import Video

        node = lxml.objectify.XML('<renditions xmlns:py="http://codespeak.net/lxml/objectify/pytype" xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <rendition url="foo" frame_width="100" video_duration="910"/>\n  <rendition url="baa" frame_width="200"  video_duration="920"/>\n</renditions>\n')

        video = Video()
        video.xml.head.renditions = node
        self.assertEqual('foo', video.renditions[0].url)
        self.assertEqual(100, video.renditions[0].frame_width)
        self.assertEqual(910, video.renditions[0].video_duration)
