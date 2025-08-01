from pendulum import datetime
import transaction

from zeit.cms.checkout.helper import checked_out
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
from zeit.content.audio.testing import AudioBuilder
import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.content.audio.audio
import zeit.content.volume.volume
import zeit.mediaservice.mediaservice
import zeit.mediaservice.testing


class TestCreateAudio(zeit.mediaservice.testing.FunctionalTestCase):
    def test_creates_audio_object(self):
        mediaservice = zeit.mediaservice.mediaservice.MediaService()
        audio = mediaservice.create_audio_object(
            1234, {'url': 'http://example.com/example.mp3', 'duration': 282}
        )
        assert audio.external_id == '1234'
        assert audio.audio_type == 'premium'
        assert audio.url == 'http://example.com/example.mp3'
        assert audio.duration == 282


class TestVolumeArticleAudios(zeit.mediaservice.testing.SQLTestCase):
    def setUp(self):
        super().setUp()
        self.create_volume(2025, 1)
        self.create_volume_content('2025', '01', 'article01')
        transaction.commit()

    def create_volume(self, year, name, product='ZEI', published=True):
        volume = zeit.content.volume.volume.Volume()
        volume.year = year
        volume.volume = name
        volume.product = zeit.cms.content.sources.Product(product)
        if published:
            volume.date_digital_published = datetime(year, name, 1)
        year = str(year)
        name = '%02d' % name
        self.repository[year] = zeit.cms.repository.folder.Folder()
        self.repository[year][name] = zeit.cms.repository.folder.Folder()
        self.repository[year][name]['ausgabe'] = volume
        return self.repository[year][name]['ausgabe']

    def create_volume_content(self, volume_year, volume_number, name, product='ZEI'):
        article = Article()
        zeit.cms.content.field.apply_default_values(article, IArticle)
        article.product = zeit.cms.content.sources.Product(product)
        article.volume = int(volume_number)
        article.year = int(volume_year)
        article.title = 'title'
        article.ressort = 'Kultur'
        article.access = 'free'
        article.ir_mediasync_id = 1234
        self.repository[volume_year][volume_number][name] = article
        info = IPublishInfo(self.repository[volume_year][volume_number][name])
        info.published = False
        info.urgent = True
        return self.repository[volume_year][volume_number][name]

    def test_article_with_premium_audio_creates_audio_object(self):
        volume = self.repository['2025']['01']['ausgabe']
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        all_content_to_publish = volume.articles_with_references_for_publishing()
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/article01')
        self.assertTrue(article.has_audio)
        audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
        self.assertIn(article, all_content_to_publish)
        self.assertIn(audio, all_content_to_publish)
        self.assertEqual(audio.title, article.title)

    def test_mediaservice_creates_premium_audio_for_published_article(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article.date_digital_published = datetime(2025, 1, 1)
        info = IPublishInfo(article)
        info.published = True
        info.date_first_released = datetime(2025, 1, 1)
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()

        article = self.repository['2025']['01']['article01']
        assert article.has_audio
        audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
        assert audio

    def test_mediaservice_creates_premium_audio_for_article_with_has_audio(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article.date_digital_published = datetime(2025, 1, 1)
        info = IPublishInfo(article)
        info.published = True
        info.date_first_released = datetime(2025, 1, 1)
        with checked_out(article, raise_if_error=True) as co:
            co.has_audio = True
        transaction.commit()
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()

        article = self.repository['2025']['01']['article01']
        assert article.has_audio
        audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
        assert audio

    def test_mediaservice_sets_has_audio_for_article_with_premium_audio(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article_uuid = zeit.cms.content.interfaces.IUUID(article).shortened
        audio_folder = zeit.cms.content.add.find_or_create_folder('premium', 'audio', '2025', '01')

        AudioBuilder().with_audio_type('premium').unique_id(
            audio_folder.uniqueId + '/' + article_uuid
        ).referenced_by(article).build()
        transaction.commit()
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()

        article = self.repository['2025']['01']['article01']
        assert article.has_audio

    def test_mediaservice_does_not_add_duplicate_references(self):
        volume = self.repository['2025']['01']['ausgabe']
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        audio_references = zeit.content.audio.interfaces.IAudioReferences(
            self.repository['2025']['01']['article01']
        )
        assert len(audio_references.get_by_type('premium')) == 1

    def test_mediaservice_does_not_recreate_audio(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article_uuid = zeit.cms.content.interfaces.IUUID(article).shortened
        audio_folder = zeit.cms.content.add.find_or_create_folder('premium', 'audio', '2025', '01')
        transaction.commit()

        AudioBuilder().with_audio_type('custom').unique_id(
            audio_folder.uniqueId + '/' + article_uuid
        ).referenced_by(article).build()
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        assert audio_folder[article_uuid].audio_type == 'custom'

    def test_mediaservice_does_not_check_out_article_unnecessarily(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article_uuid = zeit.cms.content.interfaces.IUUID(article).shortened
        audio_folder = zeit.cms.content.add.find_or_create_folder('premium', 'audio', '2025', '01')

        (
            AudioBuilder()
            .with_audio_type('premium')
            .unique_id(audio_folder.uniqueId + '/' + article_uuid)
            .referenced_by(article)
            .build()
        )

        with checked_out(article, raise_if_error=True) as co:
            co.has_audio = True

        transaction.commit()
        with checked_out(article, raise_if_error=True) as co:
            # This would fail if it would try to check out
            zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
