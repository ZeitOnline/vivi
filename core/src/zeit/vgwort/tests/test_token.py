# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.vgwort.token import _order_tokens
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


class OrderTokensTest(zeit.vgwort.testing.TestCase):

    def test_enough_tokens_should_not_order(self):
        ts = zope.component.getUtility(
            zeit.vgwort.interfaces.ITokens)
        ts.order(20)
        self.assertEqual(20, len(ts))
        _order_tokens()
        self.assertEqual(20, len(ts))

    def test_insufficient_tokens_should_order_new(self):
        ts = zope.component.getUtility(
            zeit.vgwort.interfaces.ITokens)
        self.assertEqual(0, len(ts))
        _order_tokens()
        self.assertEqual(1, len(ts))
