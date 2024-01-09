import lxml.objectify
import zope.component

import zeit.cms.testing
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.content.modules.jobticker
import zeit.edit.interfaces


class TestJobboxtickerblock(zeit.content.cp.testing.FunctionalTestCase):
    def create_jobticker_block(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        lead = cp['lead']
        return zope.component.getAdapter(
            lead, zeit.edit.interfaces.IElementFactory, name='jobbox_ticker'
        )()

    def test_feed_id_from_source_is_written_to_jobticker_block(self):
        block = self.create_jobticker_block()
        source = zeit.content.cp.interfaces.IJobTickerBlock['feed'].source
        feed = source.factory.getValues(block)[0]
        block.feed = feed
        self.assertTrue('id="{id}"'.format(id=feed.id) in zeit.cms.testing.xmltotext(block.xml))

    def test_feed_is_read_from_jobticker_block(self):
        xml = lxml.objectify.fromstring(
            """
                <container xmlns:cp="http://namespaces.zeit.de/CMS/cp"
                cp:type="jobbox_ticker" module="jobbox_ticker" id="hp"/>"""
        )
        block = self.create_jobticker_block()
        block.xml = xml
        self.assertTrue(isinstance(block.feed, zeit.content.modules.jobticker.Feed))

    def test_feed_is_read_from_jobticker_block_bbb(self):
        xml = lxml.objectify.fromstring(
            """
                <container xmlns:cp="http://namespaces.zeit.de/CMS/cp"
                cp:type="jobbox_ticker" module="jobbox_ticker"
                jobbox_ticker_id="hp"/>
                """
        )
        block = self.create_jobticker_block()
        block.xml = xml
        self.assertTrue(isinstance(block.feed, zeit.content.modules.jobticker.Feed))
