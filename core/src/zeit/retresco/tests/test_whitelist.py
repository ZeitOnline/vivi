import mock
import zeit.retresco.testing


class TestWhitelist(zeit.retresco.testing.FunctionalTestCase):
    """Testing ..whitelist.Whitelist"""

    @property
    def whitelist(self):
        from ..whitelist import Whitelist
        return Whitelist()

    def test_get_creates_tag_from_code(self):
        tag = self.whitelist.get('person:=)Wolfgang')
        self.assertEqual('Wolfgang', tag.label)
        self.assertEqual('person', tag.entity_type)

    def test_get_returns_None_for_old_uuids(self):
        self.assertEqual(
            None, self.whitelist.get('66ef0e83-f760-43fa-ae24-8bf9ce14ebf0'))

    def test_search_uses_TMS_get_keywords_for_searching(self):
        with mock.patch('zeit.retresco.connection.TMS.get_keywords') as kw:
            self.whitelist.search('Foo-Bar')
        self.assertEqual('Foo-Bar', kw.call_args[0][0])
