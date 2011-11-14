# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.vgwort.token import _order_tokens
import transaction
import unittest
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


class ObjectCopyTest(zeit.vgwort.testing.TestCase):

    def test_copying_should_removes_vgwort_properties_from_copy(self):
        import datetime
        import pytz
        import zeit.cms.interfaces
        import zeit.vgwort.interfaces
        content = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/testcontent')
        token = zeit.vgwort.interfaces.IToken(content)
        token.public_token = u'public'
        token.private_token = u'private'
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = datetime.datetime.now(pytz.UTC)
        info.reported_error = u'error'
        online = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/')
        zope.copypastemove.interfaces.IObjectCopier(content).copyTo(
            online, 'foo')
        copy = zeit.cms.interfaces.ICMSContent(
            'http://xml.zeit.de/online/foo')
        token = zeit.vgwort.interfaces.IToken(copy)
        self.assertEqual(None, token.public_token)
        self.assertEqual(None, token.private_token)
        info = zeit.vgwort.interfaces.IReportInfo(copy)
        self.assertEqual(None, info.reported_on)
        self.assertEqual(None, info.reported_error)


class TokenServiceTest(unittest.TestCase):

    def test_should_be_initializable_without_config(self):
        from zeit.vgwort.token import TokenService
        TokenService()
