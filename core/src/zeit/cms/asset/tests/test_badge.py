# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import transaction
import zeit.cms.asset.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.testing


class TestBadge(zeit.cms.testing.FunctionalTestCase):

    def test_p_changed(self):
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        co = zeit.cms.checkout.interfaces.ICheckoutManager(content).checkout()
        transaction.commit()
        self.assertTrue(co._p_jar is not None)
        self.assertFalse(co._p_changed)
        zeit.cms.asset.interfaces.IBadges(co).badges = frozenset(
            ['video', 'gallery'])
        self.assertTrue(co._p_changed)
