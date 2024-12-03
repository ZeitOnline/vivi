from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
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
