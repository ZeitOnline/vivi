# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.repository.interfaces
import zeit.cms.testing
import zeit.cms.workingcopy.interfaces
import zope.component


class TestConflicts(zeit.cms.testing.FunctionalTestCase):

    def setUp(self):
        super(TestConflicts, self).setUp()
        self.repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
        self.repository['online']['conflicting'] = (
            zeit.cms.repository.unknown.PersistentUnknownResource(u'Pop'))
        self.res = zeit.cms.workingcopy.interfaces.ILocalContent(
            self.repository['online']['conflicting'])
        self.repository['online']['conflicting'] = (
            zeit.cms.repository.unknown.PersistentUnknownResource(u'Bang'))

    def test_conflict_on_setitem(self):
        self.assertRaises(
            zeit.cms.repository.interfaces.ConflictError,
            self.repository['online'].__setitem__, 'conflicting', self.res)

    def test_conflict_on_add_content(self):
        self.assertRaises(
            zeit.cms.repository.interfaces.ConflictError,
            self.repository.addContent, self.res)

    def test_conflict_override(self):
        self.repository.addContent(self.res, ignore_conflicts=True)
        self.assertEquals(u'Pop',
                          self.repository['online']['conflicting'].data)
