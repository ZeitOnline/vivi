# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.vgwort.interfaces
import zeit.vgwort.testing
import zope.component


class WebServiceTest(zeit.vgwort.testing.EndToEndTestCase):

    def test_nonexistent_methods_should_not_confuse(self):
        service = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)
        try:
            service.non_existent
        except AttributeError, e:
            self.assertEqual(
                "Method not found: 'MessageService.MessagePort.non_existent'",
                str(e))
        else:
            self.fail('AttributeError should have been raised.')

    def test_smoketest_successful_call_roundtrip(self):
        service = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)
        result = service.qualityControl()
        self.assert_(len(result.qualityControlValues) > 0)
