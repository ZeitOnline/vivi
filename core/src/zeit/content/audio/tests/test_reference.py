from zeit.cms.testcontenttype.testcontenttype import ExampleContentType
import zeit.content.audio.testing


class ReferenceTest(zeit.content.audio.testing.FunctionalTestCase):
    def test_content_audio_references_does_not_break(self):
        self.repository['example'] = ExampleContentType()

        audioreference = zeit.content.audio.interfaces.IAudioReferences(self.repository['example'])
        self.assertEqual((), audioreference.items)
        self.assertEqual(list(), audioreference.get_by_type('podcast'))
