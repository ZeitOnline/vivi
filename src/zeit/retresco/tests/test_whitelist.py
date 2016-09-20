# coding: utf-8
from zeit.retresco.tag import Tag
import json
import mock
import zeit.cms.browser.interfaces
import zeit.cms.tagging.source
import zeit.cms.testing
import zeit.retresco.testing
import zope.component
import zope.publisher.browser


class TestWhitelist(zeit.retresco.testing.FunctionalTestCase):
    """Testing ..whitelist.Whitelist"""

    @property
    def whitelist(self):
        from ..whitelist import Whitelist
        return Whitelist()

    def test_get_creates_tag_from_code(self):
        tag = self.whitelist.get(u'person☃Wolfgang')
        self.assertEqual('Wolfgang', tag.label)
        self.assertEqual('person', tag.entity_type)

    def test_get_returns_None_for_old_uuids(self):
        self.assertEqual(
            None, self.whitelist.get('66ef0e83-f760-43fa-ae24-8bf9ce14ebf0'))

    def test_search_uses_TMS_get_keywords_for_searching(self):
        with mock.patch('zeit.retresco.connection.TMS.get_keywords') as kw:
            self.whitelist.search('Foo-Bar')
        self.assertEqual('Foo-Bar', kw.call_args[0][0])


class TestWhitelistLocationAutocomplete(
        zeit.cms.testing.ZeitCmsBrowserTestCase):
    """Testing ..whitelist.Whitelist.locations()."""

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_search_for_locations(self):
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer,
            SERVER_URL='http://localhost/++skin++vivi')
        url = zope.component.getMultiAdapter(
            (zeit.cms.tagging.source.locationSource(None), request),
            zeit.cms.browser.interfaces.ISourceQueryURL)
        with mock.patch('zeit.retresco.connection.TMS.get_locations') as gl:
            gl.return_value = [Tag(u'Schweiz', u'location'),
                               Tag(u'Frankreich', u'location')]
            b = self.browser
            b.open(url + '?term=ei')
            result = json.loads(b.contents)
        self.assertEqual([{u'label': u'Schweiz',
                           u'value': u'tag://location\\u2603Schweiz'},
                          {u'label': u'Frankreich',
                           u'value': u'tag://location\\u2603Frankreich'}],
                         result)
