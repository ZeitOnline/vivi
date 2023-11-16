# coding: utf-8
from zeit.cms.checkout.helper import checked_out
import lxml.objectify
import transaction
import zeit.cms.testing


class XMLPickleException(zeit.cms.testing.ZeitCmsTestCase):
    def test_parse_errors_are_deserialized_as_comment(self):
        with checked_out(self.repository['testcontent'], temporary=False) as co:
            co.xml.body.append(lxml.objectify.fromstring('<em eiscafé="foo"/>'))
            transaction.commit()
            co._p_invalidate()  # evict from ZODB cache and unpickle afresh
            co.uniqueId
            self.assertEllipsis(
                '<error>...value for attribute eiscaf...</error>',
                zeit.cms.testing.xmltotext(co.xml),
            )
