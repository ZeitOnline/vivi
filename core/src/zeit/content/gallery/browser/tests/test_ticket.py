import zeit.cms.testing
import zeit.content.gallery.browser.ticket
import zeit.content.gallery.testing


class TestTicketAuthorization(zeit.content.gallery.testing.FunctionalTestCase):
    rnd = -2134234234
    hash_ = 28 * b'x'

    def test_pack_unpack(self):
        packed = zeit.content.gallery.browser.ticket.pack(self.rnd, self.hash_, self.principal.id)
        unpacked = zeit.content.gallery.browser.ticket.unpack(packed)
        self.assertEqual(unpacked[0], self.rnd)
        self.assertEqual(unpacked[1], self.hash_)
        self.assertEqual(unpacked[2], self.principal.id)

    def test_ticket(self):
        ticket = zeit.content.gallery.browser.ticket.get_hash(self.rnd, self.principal.id)
        unpacked = zeit.content.gallery.browser.ticket.unpack(ticket)
        self.assertEqual(unpacked[0], self.rnd)
        self.assertNotEqual(unpacked[1], self.hash_)
        self.assertEqual(unpacked[2], self.principal.id)
