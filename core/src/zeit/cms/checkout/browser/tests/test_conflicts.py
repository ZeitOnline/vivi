"""
Conflict handling
=================

Conflicts happen for example in the following case:

1. A checks out document X
2. B checks out document X
3. B checks in document X
4. A checks in document X
"""

import lxml.etree

import zeit.cms.testing


class ConflictHandlingTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        # Make one checkout/checkin cycle to assign an etag so the conflict handling
        # actually works
        self.browser.open('http://localhost/++skin++cms/repository/testcontent')
        self.browser.getLink('Checkout').click()
        self.browser.getLink('Checkin').click()

    def test_conflict_error_shown_when_two_users_modify_same_document(self):
        self._create_conflict()
        self.assertIn('There was an error while checking in your version of', self.browser.contents)
        self.assertIn('http://xml.zeit.de/testcontent', self.browser.contents)
        self.assertIn('Last modified by', self.browser.contents)
        self.assertIn('Date last checked out', self.browser.contents)

    def test_cancel_returns_to_came_from_view(self):
        self._create_conflict()
        self.browser.getControl('Cancel').click()
        self.assertEqual(
            'http://localhost/++skin++cms/workingcopy/zope.user/testcontent/@@edit.html',
            self.browser.url,
        )

    def test_checkin_correction_anyway_ignores_conflicts(self):
        self._create_conflict()
        self.browser.getControl('Checkin correction anyway').click()
        self.assertIn(
            '"testcontent" has been checked in. Conflicts were ignored.', self.browser.contents
        )

    def test_delete_workingcopy_removes_working_copy(self):
        self._create_conflict()
        self.browser.getControl('Delete workingcopy').click()
        self.assertEqual('http://localhost/++skin++cms/repository/testcontent', self.browser.url)

    def _create_conflict(self):
        self.browser.open('http://localhost/++skin++cms/repository/testcontent')
        self.browser.getLink('Checkout').click()

        article = self.getRootFolder()['workingcopy']['zope.user']['testcontent']
        article.xml.replace(article.xml.find('body'), lxml.etree.fromstring('<body>bar</body>'))
        article._p_changed = True

        with zeit.cms.testing.interaction('zope.producer'):
            b_browser = zeit.cms.testing.Browser(self.layer['wsgi_app'])
            b_browser.login('globalmgr', 'globalmgrpw')
            b_browser.open('http://localhost/++skin++cms/repository/testcontent/@@locks.html')
            b_browser.getControl('Steal').click()
            b_browser.open('http://localhost/++skin++cms/repository/testcontent')
            b_browser.getLink('Checkout').click()

            b_article = self.getRootFolder()['workingcopy']['zope.globalmgr']['testcontent']
            b_article.xml.replace(
                b_article.xml.find('body'), lxml.etree.fromstring('<body>baz</body>')
            )
            b_article._p_changed = True
            b_browser.getLink('Checkin').click()

        self.browser.getLink('Checkin').click()
        self.assertIn('Conflict Error', self.browser.contents)
