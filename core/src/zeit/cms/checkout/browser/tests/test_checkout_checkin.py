"""
Checkin/Checkout User-Interface
===============================
"""

import traceback

import zope.component
import zope.interface

import zeit.cms.browser.interfaces
import zeit.cms.content.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.testing


class CheckoutCheckinTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    """Test checkout and checkin functionality."""

    def setUp(self):
        super().setUp()
        host = 'http://localhost/++skin++cms'
        self.content_url = f'{host}/repository/testcontent'
        self.working_copy_url = f'{host}/workingcopy/zope.user/testcontent'

    def test_repository_content_has_checkout_link_but_no_checkin_link(self):
        """Checkout is possible for Repository content. Let's open a dockument in the
        repository and look at its `metadata_preview` page. We do have a checkout link
        but no checkin link"""
        self.browser.open(f'{self.content_url}/metadata_preview')
        checkout_link = self.browser.getLink('Checkout')
        self.assertIsNotNone(checkout_link)
        # The url has information about the view where the link was generated from:
        self.assertIn('@@checkout?came_from=metadata_preview', checkout_link.url)

        with self.assertRaises(LookupError):
            self.browser.getLink('Checkin')

    def test_checkout_creates_working_copy_and_shows_message(self):
        self.browser.open(f'{self.content_url}/metadata_preview')
        self.browser.getLink('Checkout').click()

        self.assertIn('"testcontent" has been checked out.', self.browser.contents)
        self.assertIn('workingcopy', self.browser.url)

    def test_checked_out_document_has_checkin_link_but_no_checkout_link(self):
        """After checking out we see the checked out document and can check it in again.
        There is of course no checkout button any more"""
        self.browser.open(self.content_url)
        self.browser.getLink('Checkout').click()

        with self.assertRaises(LookupError):
            self.browser.getLink('Checkout')

        # The checkin link also indicates the ``came_from`` view
        checkin_link = self.browser.getLink('Checkin')
        self.assertIsNotNone(checkin_link)
        self.assertIn('@@checkin?came_from=edit.html&semantic_change=None', checkin_link.url)

        self.browser.getLink('Checkin').click()
        self.assertEqual(f'{self.content_url}/@@view.html', self.browser.url)
        self.assertIn('"testcontent" has been checked in.', self.browser.contents)

    def test_checkin_does_not_update_last_semantic_change_by_default(self):
        """The checkin default action does not update the "last semantic change" setting"""
        repository = zope.component.getUtility(zeit.cms.repository.interfaces.IRepository)
        sc = zeit.cms.content.interfaces.ISemanticChange(repository['testcontent'])
        initial_change = sc.last_semantic_change

        self.browser.open(self.content_url)
        self.browser.getLink('Checkout').click()
        self.browser.getLink('Checkin').click()

        final_change = sc.last_semantic_change
        self.assertEqual(initial_change, final_change)

    def test_checkout_adapts_to_edit_view_name(self):
        """Checkout and checkin try to redirect to a meaningful view after the
        checkout/checkin has happend.

        Checkout adapts the context to IEditViewName and uses the resulting view name
        as new view.  If there is no adapter, 'edit.html' is used; we've seen this
        above.

        Register an adapter from 'view.html' to 'foobar.html':"""
        gsm = zope.component.getGlobalSiteManager()

        def view_custom(context):
            return 'foobar.html'

        gsm.registerAdapter(
            view_custom,
            (zeit.cms.interfaces.ICMSContent,),
            zeit.cms.browser.interfaces.IEditViewName,
            name='view.html',
        )
        self.browser.open(f'{self.content_url}/@@view.html')
        self.browser.handleErrors = False
        try:
            self.browser.getLink('Checkout').click()
        except Exception:
            tb = traceback.format_exc()
            self.assertIn("http://xml.zeit.de/testcontent>, name: '@@foobar.html'", tb)
        finally:
            gsm.unregisterAdapter(
                view_custom,
                (zeit.cms.interfaces.ICMSContent,),
                zeit.cms.browser.interfaces.IEditViewName,
                name='view.html',
            )

    def test_checkin_adapts_to_display_view_name(self):
        """The checkin view adapts the context to IDisplayViewName instead of IDisplayViewName."""
        gsm = zope.component.getGlobalSiteManager()

        def edit_custom(context):
            return 'foobar.html'

        gsm.registerAdapter(
            edit_custom,
            (zeit.cms.interfaces.ICMSContent,),
            zeit.cms.browser.interfaces.IDisplayViewName,
            name='view.html',
        )

        self.browser.handleErrors = False

        self.browser.open(self.content_url)
        self.browser.getLink('Checkout').click()
        self.browser.open(f'{self.working_copy_url}/@@edit.html')
        try:
            self.browser.getLink('Checkin').click()
        except Exception:
            tb = traceback.format_exc()
            self.assertIn("http://xml.zeit.de/testcontent>, name: '@@foobar.html'", tb)
        finally:
            gsm.unregisterAdapter(
                edit_custom,
                (zeit.cms.interfaces.ICMSContent,),
                zeit.cms.browser.interfaces.IDisplayViewName,
                name='view.html',
            )

    def test_checkout_without_redirect_returns_url(self):
        """For javascript, we provide a variant that does not redirect but instead returns
        the URL. It also does not do any view calculation but returns the base URL of
        the freshly checked-out/-in object:"""
        self.browser.open(f'{self.content_url}/@@checkout?redirect=False')
        self.assertEqual(self.working_copy_url, self.browser.contents.strip())
        self.browser.open(self.working_copy_url + '/@@checkin?redirect=False&event=')

        self.assertEqual(self.content_url, self.browser.contents.strip())

    def test_checkout_already_checked_out_object_redirects_to_working_copy(self):
        """Instead of throwing an error, the @@checkout view just redirects to the already
        checked-out object."""
        self.browser.open(f'{self.content_url}/@@checkout')
        self.browser.open(f'{self.content_url}/@@checkout')
        self.assertEqual(f'{self.working_copy_url}/@@edit.html', self.browser.url)
