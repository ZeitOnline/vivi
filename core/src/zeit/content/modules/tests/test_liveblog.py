from unittest import mock
import lxml.etree
import zeit.content.modules.embed
import zeit.content.modules.testing


class ConsentInfo(zeit.content.modules.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.context = mock.Mock()
        self.context.__parent__ = None
        self.module = zeit.content.modules.liveblog.TickarooLiveblog(
            self.context, lxml.objectify.XML('<container/>')
        )

    def test_liveblog_stores_local_values_in_xml(self):
        self.module.liveblog_id = '1234'
        self.module.collapse_preceding_content = True
        assert lxml.etree.tostring(self.module.xml) == (
            b'<container liveblog_id="1234" ' b'collapse_preceding_content="True"/>'
        )
