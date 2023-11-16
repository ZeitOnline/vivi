from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.testing


class FolderPermissionsTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        self.folder = self.repository['online']['2007']['01']
        self.producing = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        self.producing.login('producer', 'producerpw')

    def test_normal_user_may_not_retract_via_menu_item(self):
        IPublishInfo(self.folder).published = True
        b = self.browser
        b.open('http://localhost/repository/online/2007/01')
        self.assertNotIn('01/@@retract', b.contents)
        self.assertNotIn('01/@@publish', b.contents)

    def test_producing_may_retract_via_menu_item(self):
        IPublishInfo(self.folder).published = True
        b = self.producing
        b.open('http://localhost/repository/online/2007/01')
        self.assertEllipsis('...<a...01/@@retract...', b.contents)
        self.assertEllipsis('...<a...01/@@publish...', b.contents)
