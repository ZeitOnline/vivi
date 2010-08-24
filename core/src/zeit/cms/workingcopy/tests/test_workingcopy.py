# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt


import zeit.cms.testing


class AdapterTests(zeit.cms.testing.FunctionalTestCase):

    def test_adapting_none_should_return_current_principals_wc(self):
        from zeit.cms.workingcopy.interfaces import IWorkingcopy
        wc = IWorkingcopy(None)
        self.assertEqual('zope.user', wc.__name__)

