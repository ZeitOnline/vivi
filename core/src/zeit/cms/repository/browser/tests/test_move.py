import zeit.cms.testing


class MoveTest(zeit.cms.testing.ZeitCmsBrowserTestCase):

    login_as = 'zmgr:mgrpw'

    def test_prefills_with_current_path(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/testcontent'
            '/@@move-box')
        self.assertEqual('/testcontent', b.getControl('New path').value)
        b.getControl('Move').click()
        self.assertEllipsis('.../testcontent... already exists...', b.contents)

    def test_moves_object(self):
        b = self.browser
        b.open(
            'http://localhost/++skin++vivi/repository/testcontent'
            '/@@move-box')
        b.getControl('New path').value = '/online/2007/01/flub'
        b.getControl('Move').click()
        self.assertEllipsis(
            '...<span class="nextURL">http://localhost/++skin++vivi/repository'
            '/online/2007/01/flub...', b.contents)
        with self.assertNothingRaised():
            zeit.cms.interfaces.ICMSContent(
                'http://xml.zeit.de/online/2007/01/flub')
