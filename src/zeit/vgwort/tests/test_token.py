# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.vgwort.interfaces
import zeit.vgwort.testing
import zope.component


class TokenStorageTest(zeit.vgwort.testing.EndToEndTestCase):

    def test_order_tokens(self):
        ts = zope.component.getUtility(
            zeit.vgwort.interfaces.ITokens)
        self.assertEqual(0, len(ts))
        ts.order(2)
        self.assertEqual(2, len(ts))
