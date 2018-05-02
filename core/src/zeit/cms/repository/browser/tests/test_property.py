from mechanize import LinkNotFoundError
import zeit.cms.testing


class DAVPropertiesListingTest(zeit.cms.testing.ZeitCmsBrowserTestCase):

    def test_not_shown_in_workingcopy(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/testcontent/@@checkout')
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
            </td>...""", b.contents)
