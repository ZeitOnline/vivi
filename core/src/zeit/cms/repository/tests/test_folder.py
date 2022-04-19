import zope.copypastemove.interfaces

import zeit.cms.testing
import zeit.cms.interfaces
import zeit.workflow.interfaces
import zeit.workflow.testing


class RenameFolderTest(zeit.cms.testing.ZeitCmsTestCase):

    def test_renaming_folder(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(
            self.repository)
        renamer.renameItem('online', 'offline')
        self.assertNotIn('online', self.repository)
        self.assertIn('offline', self.repository)


class FolderDependenciesTest(zeit.cms.testing.ZeitCmsTestCase):

    layer = zeit.workflow.testing.CELERY_LAYER

    def test_folder_dependencies(self):
        folder = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/2007')
        dependencies = list(zeit.workflow.interfaces.IPublicationDependencies(
            folder).get_dependencies())
        self.assertEqual(
            'http://xml.zeit.de/online/2007/01/', dependencies[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/online/2007/02/', dependencies[1].uniqueId)
