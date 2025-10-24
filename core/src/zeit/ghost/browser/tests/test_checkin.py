import zeit.ghost.testing


class GhostCheckinTest(zeit.ghost.testing.BrowserTestCase):
    def test_checkin_on_ghost_redirects_to_origin(self):
        """It's not supposed to, but sometimes it happens that users trigger
        the checkin link on ghosts (#7152), probably by double clicking the
        checkin link or something. To prevent unnecessary errors, we provide a
        dummy checkin view that simply redirects to the ghost's origin -- so
        "checking in" a ghost has the same visible result as checking in an
        actual working copy object, namely a redirect to the repository object.
        """

        b = self.browser
        b.open('/repository/testcontent')
        b.getLink('Checkout').click()
        checkin = b.getLink('Checkin').url
        b.getLink('Checkin').click()
        self.assertEqual('http://localhost/++skin++vivi/repository/testcontent/@@view.html', b.url)
        b.open(checkin)
        self.assertEqual('http://localhost/++skin++vivi/repository/testcontent/@@view.html', b.url)
