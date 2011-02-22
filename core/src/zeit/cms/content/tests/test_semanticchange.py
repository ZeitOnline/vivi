# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestSemanticChange(zeit.cms.testing.FunctionalTestCase):

    def get_content(self):
        from zeit.cms.testcontenttype.testcontenttype import TestContentType
        return TestContentType()

    def test_lsc_should_be_set_on_creation(self):
        from zeit.cms.content.interfaces import ISemanticChange
        import datetime
        import zope.event
        import zope.lifecycleevent
        content = self.get_content()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(content))
        sc = ISemanticChange(content)
        self.assertTrue(
            isinstance(sc.last_semantic_change, datetime.datetime))

    def test_lsc_should_not_be_set_on_copy(self):
        from zeit.cms.content.interfaces import ISemanticChange
        import zope.event
        import zope.lifecycleevent
        content = self.get_content()
        zope.event.notify(zope.lifecycleevent.ObjectCopiedEvent(
            content, content))
        sc = ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)

    def test_objects_initially_should_not_have_semantic_change(self):
        from zeit.cms.content.interfaces import ISemanticChange
        content = self.get_content()
        sc = ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)

    def test_checkin_should_set_last_semantic_change(self):
        from zeit.cms.checkout.helper import checked_out
        from zeit.cms.content.interfaces import ISemanticChange
        import datetime
        import zeit.cms.interfaces
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        sc = ISemanticChange(content)
        self.assertTrue(sc.last_semantic_change is None)
        with checked_out(content, semantic_change=True) as co:
            self.assertTrue(ISemanticChange(co).last_semantic_change is None)
        self.assertTrue(
            isinstance(sc.last_semantic_change, datetime.datetime))
