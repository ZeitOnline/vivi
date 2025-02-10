from unittest import mock

import lxml.builder

import zeit.content.modules.embed
import zeit.content.modules.testing


class ConsentInfo(zeit.content.modules.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.liveblog.TickarooLiveblog(
            self.context, lxml.builder.E.container()
        )

    def test_liveblog_stores_local_values_in_xml(self):
        self.module.liveblog_id = '1234'
        self.module.collapse_preceding_content = True
        assert lxml.etree.tostring(self.module.xml) == (
            b'<container liveblog_id="1234" collapse_preceding_content="True"/>'
        )

    def test_liveblog_stores_collapse_highlighted_events_in_xml(self):
        self.module.liveblog_id = '1234'
        self.module.collapse_highlighted_events = True
        assert lxml.etree.tostring(self.module.xml) == (
            b'<container liveblog_id="1234" collapse_highlighted_events="True"/>'
        )

    def test_liveblog_stores_teaser_timeline_events_in_xml(self):
        event_id = 'some_id'
        self.module.liveblog_id = '1234'
        assert (
            lxml.etree.tostring(self.module.xml, encoding='unicode')
            == '<container liveblog_id="1234"/>'
        )

        self.module.teaser_timeline_events = [event_id]
        assert lxml.etree.tostring(self.module.xml, encoding='unicode') == (
            '<container liveblog_id="1234">'
            f'<teaser_timeline><event>{event_id}</event></teaser_timeline>'
            '</container>'
        )

        self.module.teaser_timeline_events = []
        assert lxml.etree.tostring(self.module.xml, encoding='unicode') == (
            '<container liveblog_id="1234"><teaser_timeline/></container>'
        )
