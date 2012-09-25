# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
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


class FTestLiveUrlToContent(zeit.cms.testing.FunctionalTestCase):

    def test_get_content_from_www_is_equal_as_from_xml(self):
        import zeit.cms.interfaces
        www_content = zeit.cms.interfaces.ICMSContent(
            'http://www.zeit.de/testcontent')
        xml_content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        self.assertEqual(www_content, xml_content)


class TestLiveUrlToContent(unittest.TestCase):

    @mock.patch('zeit.cms.interfaces.ICMSContent')
    def test_first_www_is_replaced(self, ICMSContent):
        from zeit.cms.repository.repository import live_url_to_content
        live_url_to_content('http://www.foo.bar/test')
        ICMSContent.assert_called_with('http://xml.foo.bar/test')

    @mock.patch('zeit.cms.interfaces.ICMSContent')
    def test_another_www_is_not_replaced(self, ICMSContent):
        from zeit.cms.repository.repository import live_url_to_content
        live_url_to_content('http://www.foo.bar/www/test')
        ICMSContent.assert_called_with('http://xml.foo.bar/www/test')

