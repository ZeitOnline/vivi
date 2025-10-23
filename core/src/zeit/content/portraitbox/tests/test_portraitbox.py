from zeit.content.portraitbox.portraitbox import Portraitbox
import zeit.cms.references.references
import zeit.content.image.testing
import zeit.content.portraitbox.testing


class ExtractReferencesTest(zeit.content.portraitbox.testing.FunctionalTestCase):
    def test_extract_references_finds_images(self):
        self.repository['image'] = zeit.content.image.testing.create_image_group()
        portraitbox = Portraitbox()
        portraitbox.image = self.repository['image']
        references = [x['target'] for x in zeit.cms.references.references.extract(portraitbox)]
        self.assertIn(self.repository['image'], references)
