# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO
import unittest
import zeit.cms.testing
import zeit.content.gallery.browser.ticket
import zeit.content.gallery.testing
import zope.app.appsetup.product


class TestTicketAuthorization(unittest.TestCase):

    rnd = -2134234234
    hash_ = 28 * 'x'
    principal = 'prin.cipal'

    def setUp(self):
        self.config = zope.app.appsetup.product.saveConfiguration()
        config = zope.app.appsetup.product.loadConfiguration(
            StringIO.StringIO(zeit.content.gallery.testing.product_config))
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
        self.assertEquals(unpacked[0], self.rnd)
        self.assertEquals(unpacked[1], self.hash_)
        self.assertEquals(unpacked[2], self.principal)

    def test_ticket(self):
        ticket = zeit.content.gallery.browser.ticket.get_hash(
            self.rnd, self.principal)
        unpacked = zeit.content.gallery.browser.ticket.unpack(ticket)
        self.assertEquals(unpacked[0], self.rnd)
        self.assertNotEquals(unpacked[1], self.hash_)
        self.assertEquals(unpacked[2], self.principal)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTicketAuthorization))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'README.txt',
        'entry-text.txt',
        'imp.txt',
        'ticket.txt',
        'upload.txt',
        layer=zeit.content.gallery.testing.GalleryLayer))
    return suite
