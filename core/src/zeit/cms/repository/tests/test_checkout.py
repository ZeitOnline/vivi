# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class DefaultAdapterTests(zeit.cms.testing.FunctionalTestCase):

    def test_adapting_foreign_objects_should_fail_adaption(self):
        from zeit.cms.workingcopy.interfaces import ILocalContent
        import zeit.cms.interfaces
        import zope.interface

        class Content(object):
            zope.interface.implements(zeit.cms.interfaces.ICMSContent)
            uniqueId = 'testcontent://'

        content = Content()
        try:
            ILocalContent(content)
        except TypeError, e:
            self.assertEqual('Could not adapt', e.args[0])
        else:
            self.fail('TypeError not raised')

    def test_adapting_removed_objects_should_fail_adaption(self):
        from zeit.cms.workingcopy.interfaces import ILocalContent
        import zeit.cms.interfaces
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        del content.__parent__[content.__name__]
        try:
            ILocalContent(content)
        except TypeError, e:
            self.assertEqual('Could not adapt', e.args[0])
        else:
            self.fail('TypeError not raised')
