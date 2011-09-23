# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.video.testing


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
        self.assertEqual('http://stillurl', node['image'].get('src'))
