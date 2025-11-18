import transaction
import zope.copypastemove.interfaces

from zeit.cms.repository.folder import Folder
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.workflow.interfaces
import zeit.workflow.testing


class RenameFolderTest(zeit.cms.testing.ZeitCmsTestCase):
    def test_renaming_folder(self):
        self.repository['folder'] = Folder()
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(self.repository)
        renamer.renameItem('folder', 'offline')
        self.assertNotIn('folder', self.repository)
        self.assertIn('offline', self.repository)


class FolderDependenciesTest(zeit.workflow.testing.FunctionalTestCase):
    def test_folder_dependencies(self):
        self.repository['folder'] = Folder()
        folder = self.repository['folder']
        folder['01'] = ExampleContentType()
        folder['02'] = ExampleContentType()
        transaction.commit()
        dependencies = list(
            zeit.cms.workflow.interfaces.IPublicationDependencies(folder).get_dependencies()
        )
        self.assertEqual('http://xml.zeit.de/folder/01', dependencies[0].uniqueId)
        self.assertEqual('http://xml.zeit.de/folder/02', dependencies[1].uniqueId)
