import transaction
import zope.interface

from zeit.cms.checkout.helper import checked_out
from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
from zeit.content.audio.testing import AudioBuilder
from zeit.content.text.text import Text
import zeit.content.article.interfaces
import zeit.entitlements
import zeit.entitlements.testing


class Entitlements(zeit.entitlements.testing.FunctionalTestCase):
    def setUp(self):
        super().setUp()
        content = ExampleContentType()
        zope.interface.alsoProvides(content, zeit.content.article.interfaces.IArticle)
        self.repository['testarticle'] = content
        self.content = self.repository['testcontent']

    def set_properties(self, name, properties):
        with checked_out(self.repository[name]) as co:
            for key, val in properties.items():
                setattr(co, key, val)
        transaction.commit()

    def test_converts_access_to_entitlements(self):
        self.assertEqual(set(), zeit.entitlements.accepted(self.repository['testcontent']))
        self.set_properties('testcontent', {'access': 'free'})
        self.assertEqual(set(), zeit.entitlements.accepted(self.repository['testcontent']))
        self.set_properties('testcontent', {'access': 'dynamic'})
        self.assertEqual(set(), zeit.entitlements.accepted(self.repository['testcontent']))
        self.set_properties('testcontent', {'access': 'registration'})
        self.assertEqual(
            {'registration'}, zeit.entitlements.accepted(self.repository['testcontent'])
        )
        self.set_properties('testcontent', {'access': 'abo'})
        self.assertEqual({'zplus'}, zeit.entitlements.accepted(self.repository['testcontent']))

    def test_empty_for_not_commonmetadata(self):
        text = Text()
        self.assertEqual(set(), zeit.entitlements.accepted(text))

    def test_ressort_wochenmarkt_adds_entitlement(self):
        with checked_out(self.content) as co:
            co.access = 'abo'
            co.ressort = 'zeit-magazin'
            co.sub_ressort = 'wochenmarkt'
        self.assertEqual({'wochenmarkt', 'zplus'}, zeit.entitlements.accepted(self.content))

    def test_podcast_audio_reference_adds_entitlement(self):
        AudioBuilder().referenced_by(self.repository['testarticle']).build()
        with checked_out(self.repository['testarticle']) as co:
            co.access = 'abo'
        self.assertEqual(
            {'podcast', 'zplus'}, zeit.entitlements.accepted(self.repository['testarticle'])
        )

    def test_accepted_entitlements(self):
        self.set_properties(
            'testcontent', {'access': 'abo', 'accepted_entitlements': 'podcast,wochenmarkt'}
        )
        self.assertEqual(
            {'podcast', 'wochenmarkt'}, zeit.entitlements.accepted(self.repository['testcontent'])
        )
        self.set_properties('testcontent', {'access': 'abo', 'accepted_entitlements': ''})
        self.assertEqual({'zplus'}, zeit.entitlements.accepted(self.repository['testcontent']))

    def test_accepted_article_entitlements(self):
        self.set_properties('testarticle', {'access': 'abo', 'accepted_entitlements': 'podcast'})
        self.assertEqual({'podcast'}, zeit.entitlements.accepted(self.repository['testarticle']))
