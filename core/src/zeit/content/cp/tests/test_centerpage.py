# coding: utf-8
from unittest import mock
import unittest

from xmldiff.main import diff_trees
import lxml.etree
import zope.component
import zope.copypastemove.interfaces

import zeit.cms.content.sources
import zeit.cms.testcontenttype.testcontenttype
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.cp.centerpage
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces


class RenderedXMLTest(zeit.content.cp.testing.FunctionalTestCase):
    def create_teaser(self, cp):
        import zeit.edit.interfaces

        factory = zope.component.getAdapter(
            cp.body['lead'], zeit.edit.interfaces.IElementFactory, name='teaser'
        )
        return factory()

    def assertXML(self, expected, actual):
        assert diff_trees(expected, actual) == []

    def test_without_any_auto_blocks_the_rendered_xml_looks_the_same(self):
        cp = zeit.content.cp.centerpage.CenterPage()
        t1 = self.create_teaser(cp)
        self.create_teaser(cp)
        t1.insert(0, self.repository['testcontent'])

        # IRenderedXML will traverse the CenterPage and adapt contained objects
        # to their interface to create the XML. But adapting the objects may
        # add additional XML attributes, thus we have to run it once to create
        # all attributes and another time to create the final XML repr.
        zeit.content.cp.interfaces.IRenderedXML(cp)
        rendered = zeit.content.cp.interfaces.IRenderedXML(cp)
        # Retrieve original XML after additional attributes were written.
        original = cp.xml

        lxml.etree.indent(original)
        lxml.etree.indent(rendered)
        self.assertXML(original, rendered)


class TestContentIter(unittest.TestCase):
    def test_unresolveable_blocks_should_not_be_adapted(self):
        from zeit.content.cp.centerpage import cms_content_iter

        centerpage = mock.Mock()
        centerpage.values = mock.Mock(
            return_value=[mock.sentinel.block1, None, mock.sentinel.block2]
        )
        with mock.patch('zeit.edit.interfaces.IElementReferences') as ci:
            cms_content_iter(centerpage)
            self.assertEqual(2, ci.call_count)
            self.assertEqual(
                [((mock.sentinel.block1,), {}), ((mock.sentinel.block2,), {})], ci.call_args_list
            )


class CenterpageTest(zeit.content.cp.testing.FunctionalTestCase):
    def test_regression_bug_217_copying_actually_copies(self):
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        copier = zope.copypastemove.interfaces.IObjectCopier(self.repository['cp'])
        copier.copyTo(self.repository['online'])
        with self.assertNothingRaised():
            self.repository['cp']

    def test_homepage_has_different_publish_priority(self):
        cp = self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        self.assertEqual(
            zeit.cms.workflow.interfaces.PRIORITY_HIGH,
            zeit.cms.workflow.interfaces.IPublishPriority(cp),
        )
        cp.type = 'homepage'
        self.assertEqual(
            zeit.cms.workflow.interfaces.PRIORITY_HOMEPAGE,
            zeit.cms.workflow.interfaces.IPublishPriority(cp),
        )


class SeriesAvailableTest(zeit.content.cp.testing.FunctionalTestCase):
    def test_series_available(self):
        cp = self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()
        cp_series = zeit.cms.content.sources.SerieSource()(cp)
        names = [x.serienname for x in cp_series]
        # See zeit.cms.content.serie.xml
        assert 'Podcast' in names
        assert 'Notcast' not in names
