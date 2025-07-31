from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.audio.testing import AudioBuilder
import zeit.entitlements
import zeit.entitlements.testing


class Entitlements(zeit.entitlements.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.content = ExampleContentType()

    def test_converts_access_to_entitlements(self):
        self.assertEqual(set(), zeit.entitlements.accepted(self.content))
        self.content.access = 'free'
        self.assertEqual(set(), zeit.entitlements.accepted(self.content))
        self.content.access = 'dynamic'
        self.assertEqual(set(), zeit.entitlements.accepted(self.content))
        self.content.access = 'registration'
        self.assertEqual({'registration'}, zeit.entitlements.accepted(self.content))
        self.content.access = 'abo'
        self.assertEqual({'zplus'}, zeit.entitlements.accepted(self.content))

    def test_empty_for_not_commonmetadata(self):
        self.assertEqual(
            set(), zeit.entitlements.accepted(self.repository['2006']['DSC00109_2.JPG.meta'])
        )

    def test_ressort_wochenmarkt_adds_entitlement(self):
        self.content.access = 'abo'
        self.content.ressort = 'zeit-magazin'
        self.content.sub_ressort = 'wochenmarkt'
        self.assertEqual({'wochenmarkt', 'zplus'}, zeit.entitlements.accepted(self.content))

    def test_podcast_audio_reference_adds_entitlement(self):
        content = self.repository['testcontent']
        AudioBuilder().referenced_by(content).build()
        with checked_out(content) as co:
            co.access = 'abo'
        self.assertEqual(
            {'podcast', 'zplus'}, zeit.entitlements.accepted(self.repository['testcontent'])
        )

    def test_accepted_entitlements(self):
        self.content.access = 'abo'
        self.content.accepted_entitlements = 'podcast,wochenmarkt'
        self.assertEqual({'podcast', 'wochenmarkt'}, zeit.entitlements.accepted(self.content))
        self.content.accepted_entitlements = 'podcast'
        self.assertEqual({'podcast'}, zeit.entitlements.accepted(self.content))
        self.content.accepted_entitlements = ''
        self.assertEqual({'zplus'}, zeit.entitlements.accepted(self.content))
