from zeit.cms.repository.folder import Folder
from zeit.cms.workflow.interfaces import IPublishInfo
import zeit.cms.testing


class FolderPermissionsTest(zeit.cms.testing.ZeitCmsBrowserTestCase):
    def setUp(self):
        super().setUp()
        self.repository['folder'] = Folder()
        self.folder = self.repository['folder']
        self.producing = zeit.cms.testing.Browser(self.layer['wsgi_app'])
        self.producing.login('producer', 'producerpw')

    def test_normal_user_may_not_retract_via_menu_item(self):
        IPublishInfo(self.folder).published = True
        b = self.browser
        b.open('http://localhost/repository/folder')
        self.assertNotIn('folder/@@retract', b.contents)
        self.assertNotIn('folder/@@publish', b.contents)

    def test_producing_may_not_retract_via_menu_item(self):
        IPublishInfo(self.folder).published = True
        b = self.producing
        b.open('http://localhost/repository/folder')
        self.assertNotEllipsis('...<a...folder/@@retract...', b.contents)
        self.assertNotEllipsis('...<a...folder/@@publish...', b.contents)
