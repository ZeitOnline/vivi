# -*- coding: utf-8 -*-
import lxml.etree
import lxml.objectify
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component


class TestJobboxblock(zeit.content.cp.testing.FunctionalTestCase):

    def create_jobboxblock(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        lead = cp['lead']
        return zope.component.getAdapter(
            lead,
            zeit.edit.interfaces.IElementFactory,
            name='jobbox_feed')()

    def test_jobbox_id_from_source_is_written_to_jobbox_block(self):
        block = self.create_jobboxblock()
        jobbox_source_object = zeit.content.cp.interfaces.IJobboxBlock[
            'jobbox'].source.factory.getValues(block)[0]
        block.jobbox = jobbox_source_object
        self.assertTrue("jobbox_id=\"{j_id}\"".format(
            j_id=jobbox_source_object.id) in lxml.etree.tostring(
            block.xml))

    def test_jobbox_object_is_recieved_from_jobbox_block(self):
        xml = lxml.objectify.fromstring("""
                <container xmlns:cp="http://namespaces.zeit.de/CMS/cp"
                cp:type="jobbox_feed" module="jobbox_feed" jobbox_id="hp"/>
                """)
        block = self.create_jobboxblock()
        block.xml = xml
        self.assertTrue(isinstance(block.jobbox,
                                   zeit.content.cp.interfaces.Jobbox))
