# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.video.testing


class TestVideo(zeit.content.video.testing.TestCase):

    def test_videos_should_contain_subtitle_node_in_xml_even_if_none(self):
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.subtitle = None  # set explicitly
        video = factory.next()  # in repository
        self.assertEqual(
            u'', video.xml['body']['subtitle'])


class TestReference(zeit.content.video.testing.TestCase):

    def test_still_should_be_contained_in_xml_reference(self):
        import lxml.etree
        import lxml.objectify
        import zeit.cms.content.interfaces
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.video_still = 'http://stillurl'
        video = factory.next()  # in repository

        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(video)
        node = lxml.objectify.XML(
            '<block xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:py="http://codespeak.net/lxml/objectify/pytype"/>')
        updater.update(node)
        self.assertEqual('http://stillurl', node['video-still'].get('src'))

    def test_thumbnail_should_be_contained_in_xml_reference(self):
        import lxml.etree
        import lxml.objectify
        import zeit.cms.content.interfaces
        factory = zeit.content.video.testing.video_factory(self)
        video = factory.next()
        video.thumbnail = 'http://thumbnailurl'
        video = factory.next()  # in repository

        updater = zeit.cms.content.interfaces.IXMLReferenceUpdater(video)
        node = lxml.objectify.XML(
            '<block xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:py="http://codespeak.net/lxml/objectify/pytype"/>')
        updater.update(node)
        self.assertEqual('http://thumbnailurl', node['thumbnail'].get('src'))
