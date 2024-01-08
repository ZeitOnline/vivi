# coding: utf-8
from zope.testbrowser.browser import LinkNotFoundError

from zeit.cms.checkout.helper import checked_out
import zeit.cms.testing


class DAVPropertiesListingTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    login_as = 'producer:producerpw'

    def test_not_shown_in_workingcopy(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent/@@checkout')
        with self.assertRaises(LinkNotFoundError):
            b.getLink('DAV Properties')

    def test_shows_properties_via_columns(self):
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent')
        b.getLink('DAV Properties').click()
        self.assertEllipsis(
            """...<td> http://namespaces.zeit.de/CMS/meta </td>
            <td> type </td> <td> testcontenttype </td>
            <td> <span class="SearchableText">type...testcontenttype</span>
            </td>...""",
            b.contents,
        )

    def test_handles_non_ascii(self):
        with checked_out(self.repository['testcontent']) as co:
            co.ressort = 'Zeit für die Schule'
        b = self.browser
        b.open('http://localhost/++skin++vivi/repository/testcontent')
        b.getLink('DAV Properties').click()
        self.assertEllipsis('...Zeit für die Schule...', b.contents)
