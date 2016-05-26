from zeit.retresco.testing import RequestHandler as TEST_SERVER
import json
import zeit.cms.testing
import zeit.retresco.interfaces
import zeit.retresco.testing
import zope.component


class TMSTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.retresco.testing.ZCML_LAYER

    def test_get_keywords_converts_response_to_tag_objects(self):
        TEST_SERVER.response_body = json.dumps({
            'rtr_persons': ['Merkel', 'Obama'],
            'rtr_locations': ['Berlin', 'Washington'],
        })
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        result = tms.get_keywords(self.repository['testcontent'])
        self.assertEqual(['Berlin', 'Merkel', 'Obama', 'Washington'],
                         sorted([x.label for x in result]))

    def test_raises_technical_error_for_5xx(self):
        TEST_SERVER.response_code = 500
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with self.assertRaises(zeit.retresco.interfaces.TechnicalError):
            tms.get_keywords(self.repository['testcontent'])

    def test_raises_domain_error_for_4xx(self):
        TEST_SERVER.response_code = 400
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        with self.assertRaises(zeit.retresco.interfaces.TMSError):
            tms.get_keywords(self.repository['testcontent'])
