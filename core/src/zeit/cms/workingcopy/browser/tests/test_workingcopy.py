import zope.component

from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.browser.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.testing


class WorkingcopyTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def test_checkout_redirects_to_workingcopy(self):
        b = self.browser
        b.open('/workingcopy/zope.user')
        self.assertEllipsis('...No edited documents...', b.contents)
        b.open('/repository/testcontent')
        b.getLink('Checkout').click()
        self.assertEqual(
            'http://localhost/++skin++vivi/workingcopy/zope.user/testcontent/@@edit.html', b.url
        )
        self.assertEllipsis(
            '...<a href="http://localhost/++skin++vivi/workingcopy/zope.user/testcontent/@@edit.html">testcontent</a>...',
            b.contents,
        )

    def test_sidebar_is_sorted_with_last_checkout_first(self):
        self.repository['content2'] = ExampleContentType()
        b = self.browser
        b.open('/repository/testcontent/@@checkout')
        b.open('/repository/content2/@@checkout')
        self.assertEllipsis(
            """\
        ...<a href="http://localhost/++skin++vivi/workingcopy/zope.user/content2/@@edit.html">content2</a>...
        <a href="http://localhost/++skin++vivi/workingcopy/zope.user/testcontent/@@edit.html">testcontent</a>...""",
            b.contents,
        )

    def test_checkin_after_repository_was_deleted(self):
        b = self.browser
        b.open('/repository/testcontent/@@checkout')
        bookmark = b.url

        b.open('/repository/testcontent/@@delete.html')
        b.getControl('Delete').click()

        b.open(bookmark)
        b.getLink('Checkin').click()

    def test_delete_from_workingcopy(self):
        b = self.browser
        b.open('/repository/testcontent/@@checkout')
        self.assertEllipsis(
            '...lightbox_form...@@delete.html...', b.getLink('Cancel workingcopy').url
        )
        b.open('@@delete.html')
        b.getControl('Confirm delete').click()
        self.assertEqual(
            '<span class="nextURL">http://localhost/++skin++vivi/repository/testcontent</span>',
            b.contents,
        )

        b.open('/workingcopy/zope.user')
        self.assertEllipsis('...There are no objects in this folder...', b.contents)

    def test_renameable_is_deleted_from_repository_when_deleted_from_workingcopy(self):
        co = zeit.cms.checkout.interfaces.ICheckoutManager(
            self.repository['testcontent']
        ).checkout()
        zeit.cms.repository.interfaces.IAutomaticallyRenameable(co).renameable = True
        b = self.browser
        b.open('/workingcopy/zope.user/testcontent/@@delete.html')
        b.getControl('Confirm delete').click()
        self.assertNotIn('testcontent', self.repository)


class ObjectBrowserInWorkingcopyTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_default_location_of_workingcopy_delegates_to_repository(self):
        source = zope.component.getUtility(
            zeit.cms.content.interfaces.ICMSContentSource, name='all-types'
        )
        with checked_out(self.repository['testcontent']) as co:
            workingcopy = co.__parent__
            self.assertEqual(
                None,
                zope.component.queryMultiAdapter(
                    (workingcopy, source), zeit.cms.browser.interfaces.IDefaultBrowsingLocation
                ),
            )

            (
                self.assertEqual(
                    'http://xml.zeit.de/',
                    zope.component.getMultiAdapter(
                        (co, source), zeit.cms.browser.interfaces.IDefaultBrowsingLocation
                    ).uniqueId,
                ),
            )
