# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import pytz
import zeit.cms.testcontenttype.testcontenttype
import zeit.vgwort.interfaces
import zeit.vgwort.register
import zeit.vgwort.testing
import zope.component
import zope.interface


class RegisterTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super(RegisterTest, self).setUp()
        self.vgwort = zope.component.getUtility(
            zeit.vgwort.interfaces.IMessageService)

    def tearDown(self):
        self.vgwort.error = False
        super(RegisterTest, self).tearDown()

    def test_source_smoke(self):
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        result = list(source)
        self.assertEqual(3, len(result))

    def test_successful_register_should_mark_content(self):
        now = datetime.datetime.now(pytz.UTC)
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.register.register(content)
        self.assertEqual([content], self.vgwort.calls)
        reginfo = zeit.vgwort.interfaces.IRegistrationInfo(content)
        self.assertEqual(None, reginfo.register_error)
        self.assert_(reginfo.registered_on > now)

    def test_semantic_error_should_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.WebServiceError

        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.register.register(content)

        reginfo = zeit.vgwort.interfaces.IRegistrationInfo(content)
        self.assertEqual('Provoked error', reginfo.register_error)
        self.assertEqual(None, reginfo.registered_on)

    def test_technical_error_should_not_mark_content(self):
        self.vgwort.error = zeit.vgwort.interfaces.TechnicalError

        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        zeit.vgwort.register.register(content)

        reginfo = zeit.vgwort.interfaces.IRegistrationInfo(content)
        self.assertEqual(None, reginfo.register_error)
        self.assertEqual(None, reginfo.registered_on)
