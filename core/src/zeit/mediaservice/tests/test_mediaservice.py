from pendulum import datetime

from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.article.article import Article
from zeit.content.article.interfaces import IArticle
import zeit.cms.content.field
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.content.volume.volume
import zeit.mediaservice.testing


class TestVolumeArticleAudios(zeit.mediaservice.testing.SQLTestCase):
    def setUp(self):
        super().setUp()
        self.create_volume(2025, 1)
        self.create_volume_content('2025', '01', 'article01')

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
        self.assertIn(article, all_content_to_publish)
        self.assertIn(
            zeit.content.audio.interfaces.IAudioReferences(article).items[0], all_content_to_publish
        )
