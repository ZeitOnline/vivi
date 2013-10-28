# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zope.copypastemove.interfaces


class RenameFolderTest(zeit.cms.testing.FunctionalTestCase):

    def test_renaming_folder(self):
        renamer = zope.copypastemove.interfaces.IContainerItemRenamer(
            self.repository)
        renamer.renameItem('online', 'offline')
        self.assertNotIn('online', self.repository)
        self.assertIn('offline', self.repository)
