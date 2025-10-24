from pendulum import datetime
import pendulum
import transaction
import zope.i18n

from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ISemanticChange
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


class TestMediaService(zeit.mediaservice.testing.FunctionalTestCase):
    def test_creates_audio_object(self):
        mediaservice = zeit.mediaservice.mediaservice.MediaService()
        audio = mediaservice.create_audio_object(
            1234, {'url': 'http://example.com/example.mp3', 'duration': 282}
        )
        assert audio.external_id == '1234'
        assert audio.audio_type == 'premium'
        assert audio.url == 'http://example.com/example.mp3'
        assert audio.duration == 282
        assert (
            ISemanticChange(audio).last_semantic_change.diff(pendulum.now('UTC')).in_minutes() <= 1
        )

    def test_correctly_counts_zero_objects(self):
        mediaservice = zeit.mediaservice.mediaservice.MediaService()
        articles = mediaservice.create_audio_objects(zeit.content.volume.volume.Volume())
        assert 'existing_count' in articles
        assert articles['existing_count'] == 0
        assert 'created' in articles
        assert not articles['created']


class TestCreateAudioObjects(zeit.mediaservice.testing.FunctionalTestCase):
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

    def get_log_entries(self, obj):
        log = zeit.objectlog.interfaces.ILog(obj)
        entries = tuple(
            zope.i18n.interpolate(entry.message, entry.message.mapping) for entry in log.get_log()
        )
        return entries

    def test_article_with_premium_audio_creates_audio_object(self):
        volume = self.repository['2025']['01']['ausgabe']
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()
        article = zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/2025/01/article01')
        audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
        self.assertEqual(audio.title, article.title)

        entries = self.get_log_entries(volume)
        assert entries == (
            'Created 1 premium audio objects',
            'Audio objects created for the following articles: http://xml.zeit.de/2025/01/article01',
        )

    def test_mediaservice_creates_premium_audio_for_published_article(self):
        self.create_volume_content('2025', '01', 'article02')
        self.create_volume_content('2025', '01', 'article03')
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article.date_digital_published = datetime(2025, 1, 1)
        info = IPublishInfo(article)
        info.published = True
        info.date_first_released = datetime(2025, 1, 1)
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()

        for i in range(1, 4):
            article = self.repository['2025']['01'][f'article0{i}']
            audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
            assert audio

        entries = self.get_log_entries(volume)
        assert entries == (
            'Created 3 premium audio objects',
            'Audio objects created for the following articles: http://xml.zeit.de/2025/01/article01'
            ', http://xml.zeit.de/2025/01/article02, http://xml.zeit.de/2025/01/article03',
        )

    def test_mediaservice_creates_premium_audio_for_article(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article.date_digital_published = datetime(2025, 1, 1)
        info = IPublishInfo(article)
        info.published = True
        info.date_first_released = datetime(2025, 1, 1)
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()

        article = self.repository['2025']['01']['article01']
        audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
        assert audio

        entries = self.get_log_entries(volume)
        assert entries == (
            'Created 1 premium audio objects',
            'Audio objects created for the following articles: http://xml.zeit.de/2025/01/article01',
        )

    def test_mediaservice_does_not_add_duplicate_references(self):
        volume = self.repository['2025']['01']['ausgabe']
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        audio_references = zeit.content.audio.interfaces.IAudioReferences(
            self.repository['2025']['01']['article01']
        )
        assert len(audio_references.get_by_type('premium')) == 1

        entries = self.get_log_entries(volume)
        assert entries == (
            'Created 1 premium audio objects',
            'Audio objects created for the following articles: http://xml.zeit.de/2025/01/article01',
            'Created 0 premium audio objects',
        )

    def test_mediaservice_does_not_recreate_audio(self):
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article01']
        article_uuid = zeit.cms.content.interfaces.IUUID(article).shortened
        audio_folder = zeit.cms.content.add.find_or_create_folder('premium', 'audio', '2025', '01')

        AudioBuilder().with_audio_type('custom').unique_id(
            audio_folder.uniqueId + '/' + article_uuid
        ).referenced_by(article).build()
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        assert audio_folder[article_uuid].audio_type == 'custom'

        entries = self.get_log_entries(volume)
        assert entries == ('Created 0 premium audio objects',)

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

        with checked_out(article, raise_if_error=True):
            # This would fail if it would try to check out
            zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)

        entries = self.get_log_entries(volume)
        assert entries == ('Created 0 premium audio objects',)

    def test_mediaservice_skips_checked_out_articles(self):
        self.create_volume_content('2025', '01', 'article02')
        self.create_volume_content('2025', '01', 'article03')
        volume = self.repository['2025']['01']['ausgabe']
        article = self.repository['2025']['01']['article02']
        article_uuid = zeit.cms.content.interfaces.IUUID(article).shortened

        # Let's lock article02
        lock_storage = zope.component.getUtility(zope.app.locking.interfaces.ILockStorage)
        lock_storage.setLock(
            article,
            zeit.cms.locking.locking.LockInfo(
                article, 'some_other_principal', pendulum.now('UTC').add(minutes=2)
            ),
        )

        # Create audio objects
        zeit.mediaservice.mediaservice.create_audio_objects(volume.uniqueId)
        transaction.commit()

        # Audio object for article02 is created, but not referenced in the article
        article = self.repository['2025']['01']['article02']
        assert not zeit.content.audio.interfaces.IAudioReferences(article).items
        assert zeit.cms.interfaces.ICMSContent(
            f'http://xml.zeit.de/premium/audio/2025/01/{article_uuid}'
        )

        # article01 and article03 are fine
        for i in (1, 3):
            article = self.repository['2025']['01'][f'article0{i}']
            audio = zeit.content.audio.interfaces.IAudioReferences(article).items[0]
            assert audio

        entries = self.get_log_entries(volume)
        assert entries == (
            'Created 3 premium audio objects',
            'Audio objects created for the following articles: http://xml.zeit.de/2025/01/article01'
            + ', http://xml.zeit.de/2025/01/article02, http://xml.zeit.de/2025/01/article03',
            'Could not check out the following articles: http://xml.zeit.de/2025/01/article02',
        )
