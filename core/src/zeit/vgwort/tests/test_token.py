import unittest

import transaction
import zope.component

from zeit.vgwort.token import _order_tokens
import zeit.vgwort.interfaces
import zeit.vgwort.testing


class TokenStorageTest(zeit.vgwort.testing.EndToEndTestCase):
    def order(self, amount):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        try:
            ts.order(amount)
        except zeit.vgwort.interfaces.TechnicalError:
            self.skipTest('vgwort test system down')

    def test_order_tokens(self):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        self.assertEqual(0, len(ts))
        self.order(2)
        self.assertEqual(2, len(ts))

    def test_order_should_add_str(self):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        self.order(1)
        self.assertTrue(isinstance(ts._data[0][0], str))
        self.assertTrue(isinstance(ts._data[0][0], str))


class OrderTokensTest(zeit.vgwort.testing.TestCase):
    def test_enough_tokens_should_not_order(self):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        ts.order(20)
        self.assertEqual(20, len(ts))
        _order_tokens()
        self.assertEqual(20, len(ts))

    def test_insufficient_tokens_should_order_new(self):
        ts = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
        self.assertEqual(0, len(ts))
        _order_tokens()
        self.assertEqual(1, len(ts))


class TokenTransactionTest(zeit.vgwort.testing.TestCase):
    layer = zeit.vgwort.testing.XMLRPC_LAYER

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

        content = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/testcontent')
        token = zeit.vgwort.interfaces.IToken(content)
        token.public_token = 'public'
        token.private_token = 'private'
        info = zeit.vgwort.interfaces.IReportInfo(content)
        info.reported_on = datetime.datetime.now(pytz.UTC)
        info.reported_error = 'error'
        online = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/')
        zope.copypastemove.interfaces.IObjectCopier(content).copyTo(online, 'foo')
        copy = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/foo')
        token = zeit.vgwort.interfaces.IToken(copy)
        self.assertEqual(None, token.public_token)
        self.assertEqual(None, token.private_token)
        info = zeit.vgwort.interfaces.IReportInfo(copy)
        self.assertEqual(None, info.reported_on)
        self.assertEqual(None, info.reported_error)


class SecurityObjectCopyTest(zeit.vgwort.testing.BrowserTestCase):
    def test_copying_should_work_even_with_security_on(self):
        # see #9960
        self.browser.handleErrors = False
        self.assertNothingRaised(
            self.browser.open,
            'http://localhost/++skin++vivi/repository/online/@@copy?unique_id='
            'http%3A%2F%2Fxml.zeit.de%2Fonline%2F2007%2F01%2FSomalia',
        )


class TokenServiceTest(unittest.TestCase):
    def test_should_be_initializable_without_config(self):
        from zeit.vgwort.token import TokenService

        TokenService()
