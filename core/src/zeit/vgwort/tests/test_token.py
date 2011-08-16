# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.vgwort.token import _order_tokens
import transaction
import zeit.vgwort.interfaces
import zeit.vgwort.testing
import zope.component


class TokenStorageTest(zeit.vgwort.testing.EndToEndTestCase):

    def test_order_tokens(self):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        self.assertEqual(0, len(ts))
        ts.order(2)
        self.assertEqual(2, len(ts))

    def test_order_should_add_str(self):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        ts.order(1)
        self.assertTrue(isinstance(ts._data[0][0], str))
        self.assertTrue(isinstance(ts._data[0][0], str))


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


class TokenTransactionTest(zeit.vgwort.testing.TestCase):

    def setUp(self):
        super(TokenTransactionTest, self).setUp()
        zope.security.management.endInteraction() # needed for xmlrpc

    def test_error_during_publish_still_marks_token_as_claimed(self):
        tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        tokens.order(1)
        self.assertEqual(1, len(tokens))
        transaction.commit()

        tokens.claim_immediately()

        # if an error occurs during publishing, the transaction will be aborted
        transaction.abort()
        self.assertEqual(0, len(tokens))
