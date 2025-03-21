from unittest import mock

import zeit.cms.testing


class ListingTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_columns_ignore_exceptions(self):
        with mock.patch(
            'zeit.cms.testcontenttype.testcontenttype.ExampleContentType.copyrights',
            new=mock.PropertyMock,
        ) as copyright:
            copyright.side_effect = RuntimeError('provoked')
            b = self.browser
            b.handleErrors = False
            with self.assertNothingRaised():
                b.open('http://localhost/++skin++vivi/repository')
            # Check that the cells are present but empty.
            self.assertEllipsis(
                '...<td> <span class="filename">testcontent</span> </td> <td> </td> <td> </td>...',
                b.contents,
            )
