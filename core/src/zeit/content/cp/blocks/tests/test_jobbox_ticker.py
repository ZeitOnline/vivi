import lxml.etree
import lxml.objectify
import zeit.cms.content.sources
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component


class TestJobboxtickerblock(zeit.content.cp.testing.FunctionalTestCase):

    def create_jobboxblock(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        lead = cp['lead']
        return zope.component.getAdapter(
            lead,
            zeit.edit.interfaces.IElementFactory,
            name='jobbox_ticker')()

    def test_jobbox_id_from_source_is_written_to_jobbox_ticker_block(self):
        block = self.create_jobboxblock()
        jobbox_source_object = zeit.content.cp.interfaces.IJobboxTickerBlock[
            'jobbox_ticker'].source.factory.getValues(block)[0]
        block.jobbox_ticker = jobbox_source_object
        self.assertTrue("jobbox_ticker_id=\"{j_id}\"".format(
            j_id=jobbox_source_object.id) in lxml.etree.tostring(
            block.xml))

    def test_jobbox_object_is_recieved_from_jobbox_ticker_block(self):
        xml = lxml.objectify.fromstring("""
                <container xmlns:cp="http://namespaces.zeit.de/CMS/cp"
                cp:type="jobbox_ticker" module="jobbox_ticker"
                jobbox_ticker_id="hp"/>
                """)
        block = self.create_jobboxblock()
        block.xml = xml
        self.assertTrue(isinstance(block.jobbox_ticker,
                                   zeit.cms.content.sources.JobboxTicker))
