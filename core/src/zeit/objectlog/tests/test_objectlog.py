# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from datetime import datetime
import transaction
import zeit.objectlog.interfaces
import zeit.objectlog.testing
import zope.app.component.hooks
import zope.app.testing.functional
import zope.publisher.browser
import zope.security.management
import zope.security.testing


class ObjectLog(zope.app.testing.functional.FunctionalTestCase):

    layer = zeit.objectlog.testing.ObjectLogLayer

    def setUp(self):
        super(ObjectLog, self).setUp()
        zope.app.component.hooks.setSite(self.getRootFolder())
        request = zope.publisher.browser.TestRequest()
        zope.security.management.newInteraction(request)
        request.setPrincipal(zope.security.testing.Principal(u'test.hans'))
        self.content = zeit.objectlog.testing.Content()
        self.getRootFolder()['content'] = self.content
        transaction.commit()

    def tearDown(self):
        zope.app.component.hooks.setSite(None)
        zope.security.management.endInteraction()
        super(ObjectLog, self).tearDown()

    def test_timestamp_can_be_overridden(self):
        log = zeit.objectlog.interfaces.ILog(self.content)
        log.log('foo', timestamp=datetime(2012, 6, 12, 13, 49))
        entries = list(log.get_log())
        self.assertEqual(datetime(2012, 6, 12, 13, 49), entries[-1].time)
