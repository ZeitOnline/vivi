from unittest.mock import Mock

import zope.interface.verify

from zeit.cms.checkout.helper import checked_out
from zeit.cms.workflow.interfaces import CAN_PUBLISH_ERROR
from zeit.content.audio.interfaces import Podcast, PodcastSource
from zeit.content.audio.testing import AudioBuilder, FunctionalTestCase
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.testing
import zeit.cms.workflow.interfaces
import zeit.content.audio.audio
import zeit.content.image.interfaces


class PodcastSourceTest(FunctionalTestCase):
    def test_podcast_source(self):
        podcast_source = PodcastSource().factory
        context = Mock()
        values = podcast_source.getValues(context)
        assert len(values) == 1
        distribution_channels = {
            'itunes': 'http://example.com/itunes',
            'google': 'http://example.com/google',
        }
        podcast = Podcast(
            'cat-jokes-pawdcast',
            'Cat Jokes Pawdcast',
            '1234',
            'A podcast of cat jokes',
            'e5ded8',
            'http://xml.zeit.de/2006/DSC00109_2.JPG',
            distribution_channels,
            'https://feeds.example.com/aRDC72E_',
            True,
            'Author Mc Cat Face',
            'News',
            'serial',
            'https://rss_image',
        )
        assert values[0] == podcast

    def test_audio_provides_ICommonMetadata(self):
        audio = zeit.content.audio.audio.Audio()
        zope.interface.verify.verifyObject(zeit.cms.content.interfaces.ICommonMetadata, audio)
        # Returns default values for not applicable properties
        self.assertEqual((), audio.authorships)

    def test_get_podcast_image(self):
        audio = AudioBuilder().build(self.repository)
        images = zeit.content.image.interfaces.IImages(audio)
        assert images.image.uniqueId == 'http://xml.zeit.de/2006/DSC00109_2.JPG'
        assert (
            images.fill_color == 'e5ded8'
        ), 'Fill color should match color audio/tests/fixtures/podcasts.xml'


class WorkflowTest(FunctionalTestCase):
    def test_podcast_not_published_if_requirements_not_met_url(self):
        audio = AudioBuilder().with_url('').build(self.repository)
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(audio)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        assert 'Audio URL is missing' in workflow.error_messages[0]

    def test_podcast_not_published_if_requirements_not_met_is_published(self):
        audio = AudioBuilder().with_is_published(False).build(self.repository)
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(audio)
        assert workflow.can_publish() == zeit.cms.workflow.interfaces.CAN_PUBLISH_ERROR
        assert 'Podcast Episode is not published by Provider' in workflow.error_messages[0]

    def test_podcast_not_retracted_if_requirements_not_met_is_not_published(self):
        audio = AudioBuilder().build(self.repository)
        workflow = zeit.cms.workflow.interfaces.IPublishInfo(audio)
        assert workflow.can_retract() == zeit.cms.workflow.interfaces.CAN_RETRACT_ERROR
        assert 'Podcast Episode is published by Provider' in workflow.error_messages[0]


class SpeechTest(FunctionalTestCase):
    def setUp(self):
        super().setUp()
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        uuid = zeit.cms.content.interfaces.IUUID(article).shortened
        AudioBuilder().with_audio_type('tts').with_article_uuid(uuid).build(self.repository)

    def test_create_tts_audio(self):
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/online/2007/01/Somalia')
        uuid = zeit.cms.content.interfaces.IUUID(article)
        audio = self.repository['audio']
        speechinfo = zeit.content.audio.interfaces.ISpeechInfo(audio)
        self.assertEqual(audio.audio_type, 'tts')
        self.assertEqual(speechinfo.article_uuid, uuid.shortened)
        self.assertEqual(speechinfo.preview_url, 'https://example-preview-url.bert')
        self.assertTrue(speechinfo.checksum, '123foo')

    def test_publish_tts_audio(self):
        audio = self.repository['audio']
        zeit.cms.workflow.interfaces.IPublish(audio).publish(background=False)
        assert zeit.cms.workflow.interfaces.IPublishInfo(audio).published

    def test_cannot_publish_tts_without_url(self):
        audio = self.repository['audio']
        with checked_out(audio) as co:
            co.url = ''
        assert zeit.cms.workflow.interfaces.IPublishInfo(audio).can_publish() == CAN_PUBLISH_ERROR
