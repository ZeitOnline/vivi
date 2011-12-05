# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import lxml.objectify
import zeit.cms.content.interfaces
import zeit.content.video.testing


class TestVideo(zeit.content.video.testing.TestCase):

    def test_videos_should_contain_subtitle_node_in_xml_even_if_none(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.subtitle = None  # set explicitly
        video = factory.next()  # in repository
        self.assertEqual(
            u'', video.xml['body']['subtitle'])

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
        video = factory.next() # video is now in repository['video']

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
