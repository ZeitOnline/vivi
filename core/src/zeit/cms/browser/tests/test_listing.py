import mock
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.testing
import zope.component
import zope.publisher.browser


class HitColumnTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_sort_key(self):
        class FakeAccessCounter(object):
            hits = 5
            total_hits = 19

            def __init__(self, context):
                pass

        zope.component.getSiteManager().registerAdapter(
            FakeAccessCounter, (zeit.cms.interfaces.ICMSContent,),
            zeit.cms.content.interfaces.IAccessCounter)
        listrep = zope.component.queryMultiAdapter(
            (self.repository['testcontent'],
             zope.publisher.browser.TestRequest()),
            zeit.cms.browser.interfaces.IListRepresentation)
        column = zeit.cms.browser.listing.HitColumn()
        self.assertEquals((19, 5), column.getSortKey(listrep, formatter=None))


class ListingTest(zeit.cms.testing.ZeitCmsBrowserTestCase):

    def test_columns_ignore_exceptions(self):
        with mock.patch(
                'zeit.cms.testcontenttype.testcontenttype.'
                'ExampleContentType.authors', new=mock.PropertyMock) as author:
            author.side_effect = RuntimeError('provoked')
            b = self.browser
            b.handleErrors = False
            with self.assertNothingRaised():
                b.open('http://localhost/++skin++vivi/repository')
            # Check that the cells are present but empty.
            self.assertEllipsis(
                '...<td> <span class="filename">testcontent</span> </td>'
                ' <td> 2008 ... </td> <td> </td> <td> </td> <td> </td>...',
                b.contents)
