import pytest
import transaction
import zope.security.management

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.interfaces import ICMSContent
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.content.audio.interfaces import IAudioReferences, ISpeechInfo
from zeit.content.audio.testing import AudioBuilder
from zeit.speech.connection import Speech
from zeit.speech.testing import TTS_CREATED, TTS_DELETED, FunctionalTestCase
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.mock


class TestSpeech(FunctionalTestCase):
    def test_message_audio_created(self):
        assert ICMSContent(self.unique_id, None) is None
        audio = self.create_audio(TTS_CREATED)

        assert audio.url == TTS_CREATED['articlesAudio'][0]['audioEntry']['url']
        assert audio.duration == 65
        assert ISpeechInfo(audio).article_uuid == TTS_CREATED['uuid']
        assert ISpeechInfo(audio).checksum == TTS_CREATED['articlesAudio'][0]['checksum']
        assert (
            ISpeechInfo(audio).preview_url == TTS_CREATED['articlesAudio'][1]['audioEntry']['url']
        )
        assert IPublishInfo(audio).published, 'Publish you fool!'

    def test_update_existing_tts_audio(self):
        audio = self.create_audio(TTS_CREATED)
        created_time = ISemanticChange(audio).last_semantic_change
        assert ISpeechInfo(audio).checksum == TTS_CREATED['articlesAudio'][0]['checksum']
        tts_msg = self.setup_speech_message(
            'audioEntry', {'url': 'http://example.com/cats.mp3', 'duration': 1000}
        )
        Speech().update(tts_msg)
        transaction.commit()
        updated_time = ISemanticChange(audio).last_semantic_change
        assert updated_time > created_time, 'Semantic time should be updated'
        audio = ICMSContent(self.unique_id)
        assert audio.duration == 1

    def test_update_broken_audio_repairs_reference_to_article(self):
        audio = Speech()._create(TTS_CREATED)
        IPublish(audio).publish(background=False)
        transaction.commit()
        assert ICMSContent(self.unique_id)
        assert not IAudioReferences(ICMSContent(self.article_uid)).items
        Speech().update(TTS_CREATED)
        transaction.commit()
        assert IAudioReferences(ICMSContent(self.article_uid)).items == (audio,)

    def test_article_has_corresponding_tts_audio_after_publish(self):
        original_date = IPublishInfo(self.article).date_last_published
        self.create_audio(TTS_CREATED)
        article = ICMSContent(self.article_uid)
        audio = IAudioReferences(article)
        assert audio.items == (ICMSContent(self.unique_id),)
        new_date = IPublishInfo(self.article).date_last_published
        assert new_date > original_date, 'Publishing should update date_last_published'

    def test_no_audio_for_locked_article(self):
        article = ICMSContent(self.article_uid)
        zope.security.management.endInteraction()
        with zeit.cms.testing.interaction('zope.producer'):
            zeit.cms.checkout.interfaces.ICheckoutManager(article).checkout()
        with pytest.raises(zeit.cms.checkout.interfaces.CheckinCheckoutError):
            with zeit.cms.testing.interaction('zope.user'):
                self.create_audio(TTS_CREATED)

    def test_update_audio_without_touching_the_article(self):
        audio = self.create_audio(TTS_CREATED)
        article = ICMSContent(self.article_uid)
        assert zeit.cms.workflow.mock._publish_count[article.uniqueId] == 2
        assert zeit.cms.workflow.mock._publish_count[audio.uniqueId] == 1

        Speech().update(TTS_CREATED)
        transaction.commit()
        article = ICMSContent(self.article_uid)
        audio = ICMSContent(self.unique_id)
        assert zeit.cms.workflow.mock._publish_count[article.uniqueId] == 2
        assert zeit.cms.workflow.mock._publish_count[audio.uniqueId] == 2

    def test_if_article_changed_do_not_republish_article(self):
        IPublish(self.article).publish(background=False)
        with checked_out(self.article) as co:
            paragraph = co.body.create_item('p')
            paragraph.text = 'the article has changed'
        audio = self.create_audio(TTS_CREATED)
        article = ICMSContent(self.article_uid)
        reference = IAudioReferences(article)
        assert audio in reference.items
        assert zeit.cms.workflow.mock._publish_count[audio.uniqueId] == 0
        assert zeit.cms.workflow.mock._publish_count[article.uniqueId] == 2

    def test_update_audio_still_works_even_if_article_changed(self):
        audio = self.create_audio(TTS_CREATED)
        article = ICMSContent(self.article_uid)
        reference = IAudioReferences(article)
        assert audio in reference.items
        with checked_out(self.article) as co:
            paragraph = co.body.create_item('p')
            paragraph.text = 'the article has changed'
        transaction.commit()
        Speech().update(TTS_CREATED)

    def test_handle_delete_event(self):
        self.create_audio(TTS_CREATED)
        Speech().delete(TTS_DELETED)
        transaction.commit()
        assert ICMSContent(self.unique_id, None) is None

    def test_handle_delete_event_for_non_existing_audio(self):
        Speech().delete(TTS_DELETED)
        transaction.commit()
        assert ICMSContent(self.unique_id, None) is None

    def test_remove_audio_from_article(self):
        audio = self.create_audio(TTS_CREATED)
        assert IAudioReferences(ICMSContent(self.article_uid)).items == (audio,)
        podcast = AudioBuilder().referenced_by(self.article).build()
        assert IAudioReferences(ICMSContent(self.article_uid)).items == (audio, podcast)
        Speech().delete(TTS_DELETED)
        transaction.commit()
        article = ICMSContent(self.article_uid)
        audio = IAudioReferences(article)
        assert audio.items == (podcast,)

    def test_unable_to_remove_anything_because_article_is_missing(self):
        del self.repository['article']
        transaction.commit()
        audio = AudioBuilder().with_audio_type('tts').build()
        Speech().delete(TTS_DELETED)
        transaction.commit()
        assert f'No article found for {audio}' in self.caplog.text
        assert 'audio' not in self.repository
