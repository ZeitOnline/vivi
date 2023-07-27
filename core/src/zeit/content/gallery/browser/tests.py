from io import StringIO
import unittest
import zeit.cms.testing
import zeit.content.gallery.browser.ticket
import zeit.content.gallery.testing
import zope.app.appsetup.product


class TestTicketAuthorization(unittest.TestCase):

    rnd = -2134234234
    hash_ = 28 * b'x'
    principal = 'prin.cipal'

    def setUp(self):
        self.config = zope.app.appsetup.product.saveConfiguration()
        config = zope.app.appsetup.product.loadConfiguration(
            StringIO(zeit.content.gallery.testing.product_config))
        config = [
            zope.app.appsetup.product.FauxConfiguration(name, values)
            for name, values in config.items()]
        zope.app.appsetup.product.setProductConfigurations(config)

    def tearDown(self):
        zope.app.appsetup.product.restoreConfiguration(self.config)

    def test_pack_unpack(self):
        packed = zeit.content.gallery.browser.ticket.pack(
            self.rnd, self.hash_, self.principal)
        unpacked = zeit.content.gallery.browser.ticket.unpack(packed)
        self.assertEqual(unpacked[0], self.rnd)
        self.assertEqual(unpacked[1], self.hash_)
        self.assertEqual(unpacked[2], self.principal)

    def test_ticket(self):
        ticket = zeit.content.gallery.browser.ticket.get_hash(
            self.rnd, self.principal)
        unpacked = zeit.content.gallery.browser.ticket.unpack(ticket)
        self.assertEqual(unpacked[0], self.rnd)
        self.assertNotEqual(unpacked[1], self.hash_)
        self.assertEqual(unpacked[2], self.principal)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTicketAuthorization))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'entry-text.txt',
        'crop.txt',
        'ticket.txt',
        'upload.txt',
        layer=zeit.content.gallery.testing.WSGI_LAYER))
    return suite
