import json
import zeit.cms.browser.interfaces
import zeit.cms.testing
import zope.publisher.browser


class LocationAutocompleteTest(zeit.cms.testing.ZeitCmsBrowserTestCase):

    def test_search_endtoend(self):
        request = zope.publisher.browser.TestRequest(
            skin=zeit.cms.browser.interfaces.ICMSLayer,
            SERVER_URL='http://localhost/++skin++vivi')
        url = zope.component.getMultiAdapter(
            (zeit.cms.tagging.source.locationSource(None), request),
            zeit.cms.browser.interfaces.ISourceQueryURL)
        b = self.browser
        b.open(url + '?term=NNO')
        result = json.loads(b.contents)
        self.assertEqual(
            [{'label': 'Hannover', 'value': 'tag://test\\u2603Hannover'}],
            result)
