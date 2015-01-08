import zeit.cms.testing
import zope.copypastemove.interfaces


class RenameFolderTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_renaming_folder(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(
            self.repository)
        renamer.renameItem('online', 'offline')
        self.assertNotIn('online', self.repository)
        self.assertIn('offline', self.repository)
