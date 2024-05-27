from collections import defaultdict
from time import time
import importlib.resources
import json
import logging

from lxml import etree
from transaction.interfaces import IDataManagerSavepoint, ISavepointDataManager
from zope.cachedescriptors.property import Lazy as cachedproperty
import grokcore.component as grok
import pendulum
import transaction
import zope.component
import zope.interface

from zeit.cms.content.interfaces import ISemanticChange
from zeit.cms.workflow.interfaces import IPublish, IPublishInfo
from zeit.connector.search import SearchVar
from zeit.content.article.article import Article
import zeit.cms.celery
import zeit.cms.content.add
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.sources
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.image.image
import zeit.content.image.imagegroup
import zeit.newsimport.metrics as metrics
import zeit.retresco.update
import zeit.workflow.interfaces


log = logging.getLogger(__name__)

DPA_IMPORT_SCHEMA_NS = 'http://namespaces.zeit.de/CMS/dpa'
URN = SearchVar('urn', DPA_IMPORT_SCHEMA_NS)
DOC_ID = SearchVar('doc-id', 'http://namespaces.zeit.de/CMS/import')


@grok.implementer(zeit.newsimport.interfaces.IDPANews)
class NewsProperties(zeit.cms.content.dav.DAVPropertiesAdapter):
    zeit.cms.content.dav.mapProperties(
        zeit.newsimport.interfaces.IDPANews,
        DPA_IMPORT_SCHEMA_NS,
        ('urn', 'version', 'pubstatus', 'updated'),
    )


class RubricSource(zeit.cms.content.sources.CachedXMLBase):
    product_configuration = 'zeit.newsimport'
    config_url = 'dpa-rubric-config-source'
    default_filename = 'dpa-product-id-mapping.xml'

    def get_product_id(self, pid):
        try:
            tree = self._get_tree()
            return tree.xpath('//*[contains("%s", @id)]' % pid)[1].text.strip()
        except (IndexError, KeyError):
            return 'News'  # Historical ID for "dpa", see products.xml.


RUBRIC_SOURCE = RubricSource()


class Entry:
    def __init__(self, entry):
        self.entry = entry

    @staticmethod
    def from_entry(entry):
        cls = ArticleEntry if entry['article_html'] else ImageEntry
        return cls(entry)

    @cachedproperty
    def urn(self):
        return self.entry['urn']

    @cachedproperty
    def date(self):
        # NOTE date of last semantic change
        return pendulum.parse(self.entry['version_created'])

    @cachedproperty
    def dpa_version(self):
        return self.entry['version']

    @cachedproperty
    def usable(self):
        return self.entry['pubstatus'] == 'usable'

    @cachedproperty
    def folder(self):
        date = pendulum.parse(self.entry['version_created'])
        year_month = '{0.year:04d}-{0.month:02d}'.format(date)
        day = '{0.day:02d}'.format(date)
        return zeit.cms.content.add.find_or_create_folder('news', year_month, day)

    def do_import(self):
        content = self.find_existing_content(self.urn)
        if content:
            self.update(content)
        else:
            log.info('Create %s for %s', self.__class__.__name__, self.urn)
            content = self.create()
        if not content:
            return None
        self.publish(content)
        return content

    def create(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def find_existing_content(self, urn):
        """
        Find existing content checking both namespaces to account for change in
        name.
        """
        connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)

        result = list(connector.search([URN], (URN == str(urn))))

        if len(result) == 0:
            doc_id = urn.replace(':', '-')
            result = list(connector.search([DOC_ID], (DOC_ID == str(doc_id))))

        if len(result) > 1:
            log.warning('Multiple results found for id: %s', urn)
            for item in result:
                log.warning('%s: %s', urn, item[0])

        if not result:
            return None

        try:
            content = zeit.cms.interfaces.ICMSContent(result[0][0])
            log.debug('Content %s found for %s.', content.uniqueId, urn)
            return content
        except TypeError as error:
            log.error('Content %s found for %s. But not found in DAV: %s', result[0][0], urn, error)
            return None

    def publish(self, content):
        info = IPublishInfo(content)
        info.date_last_published_semantic = self.date
        info.corrected = True
        info.edited = True
        semantic = ISemanticChange(content)
        semantic.last_semantic_change = self.date

        IPublish(content).publish(background=False)

        return content

    def has_changes(self, content):
        version = zeit.newsimport.interfaces.IDPANews(content).version
        if not version or version < self.dpa_version:
            return True
        dlps = IPublishInfo(content).date_last_published_semantic
        if not dlps or dlps < self.date:
            return True
        updated = zeit.newsimport.interfaces.IDPANews(content).updated
        if not updated or updated < pendulum.parse(self.entry['updated']):
            return True
        log.info('No changes found, skip updating %s', content)
        return False


class ArticleEntry(Entry):
    package = 'zeit.newsimport'
    resource = 'body_template.xsl'

    @cachedproperty
    def filename(self):
        return zeit.cms.interfaces.normalize_filename(self.entry['headline'])

    @cachedproperty
    def product_id(self):
        name = self.entry['rubric_names'][0]
        return RUBRIC_SOURCE.get_product_id(name)

    @cachedproperty
    def agency(self):
        return zeit.cms.interfaces.ICMSContent('http://xml.zeit.de/autoren/dpa')

    @cachedproperty
    def supertitle(self):
        supertitle = self.entry['kicker']
        if supertitle:
            return supertitle
        # Fallback to keywords
        keywords = defaultdict(list)
        for category in self.entry['categories']:
            keywords[category['type'].replace('dnltype:', '')].append(category['name'])
        for typ in ['dpasubject', 'keyword', 'geosubject']:
            if keywords[typ]:
                return keywords[typ][0]
        # NOTE last ressort: byline
        byline = self.entry['byline']
        if byline:
            return byline
        return ''

    def put_table_in_box(self, article):
        table_paths = article.xml.xpath('//body//table')
        for table_path in table_paths:
            table_parent = table_path.getparent()
            pos = table_parent.index(table_path)
            box_block = article.body.create_item('box', pos)
            # Using subtitle, since it provides markdown/pandoc to make it
            # editable manually later on.
            box_block.subtitle = etree.tostring(table_path, encoding=str)
            box_block.layout = 'news-table'
            # Remove raw table after we wrapped it inside a block
            table_parent.remove(table_path)

    def set_body(self, article):
        if not self.entry['article_html']:
            return
        root = etree.fromstring(self.entry['article_html'])
        content = etree.XSLT(
            etree.parse(str(importlib.resources.files(self.package).joinpath(self.resource)))
        )(root)

        division = article.body.xml.find('division')
        article.body.xml.replace(division, content.getroot())

    def add_topicbox(self, article):
        topicbox = article.body.create_item('topicbox', 1)
        topicbox.supertitle = 'Aktuelles'
        topicbox.title = 'Schlagzeilen'

        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        topicbox.link = '{}/news/index'.format(config['live-prefix'].rstrip('/'))
        topicbox.link_text = 'Mehr Schlagzeilen'
        topicbox.automatic_type = 'related-api'
        topicbox.topicpage_filter = 'dpa-import'

    def add_main_image(self, article):
        news = zeit.newsimport.news.Image(self.entry, article)
        image = news.do_import()
        if image is not None:
            article.main_image = article.main_image.create(image)
            teaser_image = zeit.content.image.interfaces.IImages(article)
            teaser_image.image = image

    def add_autopublish_notice(self, article):
        notice = article.body.create_item('p', len(article.body.values()))
        notice.text = self.entry['autopublishnotice']

    def apply_to_cms(self, article):
        with zeit.cms.checkout.helper.checked_out(article) as co:
            co.supertitle = self.supertitle
            co.title = self.entry['headline']
            co.channels = (('News', None),)
            co.ressort = 'News'
            co.agencies = (self.agency,)

            co.banner = True
            co.audio_speechbert = False
            co.commentSectionEnable = False
            co.commentsAllowed = False
            co.lead_candidate = False

            co.product = self.product_id

            self.set_body(co)
            self.put_table_in_box(co)
            self.add_topicbox(co)
            self.add_main_image(co)
            self.add_autopublish_notice(co)

            news_properties = zeit.newsimport.interfaces.IDPANews(co)
            news_properties.urn = self.entry['urn']
            news_properties.version = self.entry['version']
            news_properties.pubstatus = self.entry['pubstatus']
            news_properties.updated = pendulum.parse(self.entry['updated'])

    def create(self):
        folder = self.folder
        folder[self.filename] = Article()
        self.apply_to_cms(folder[self.filename])
        info = IPublishInfo(folder[self.filename])
        info.date_first_released = self.date

        return folder[self.filename]

    def retract(self):
        article = self.find_existing_content(self.urn)
        if not article:
            return None
        IPublish(article).retract(background=False)
        if zeit.cms.content.sources.FEATURE_TOGGLES.find('dpa_import_delete_image'):
            if article.main_image is not None:
                Image(self.entry, article).delete()
        return article

    def update(self, article):
        if zeit.cms.content.sources.FEATURE_TOGGLES.find('dpa_import_delete_image'):
            if article.main_image.target and not self.entry.get('associations', None):
                Image(self.entry, article).delete()
        if not self.has_changes(article):
            return None
        log.info('Update %s', article)
        unique_id = article.uniqueId
        self.apply_to_cms(article)
        article = zeit.cms.interfaces.ICMSContent(unique_id)

        return article

    def publish(self, content):
        # Checkin will trigger an asynchronous celery job for TMS (when our
        # transaction is committed by the mainloop), but that will run only
        # _long after_ our synchronous publish has run, resulting in no
        # keywords in the published TMS data. Thus we have to do it explicitly
        # and synchronously here.
        zeit.retresco.update.index_async(content.uniqueId)
        return super().publish(content)


class ImageEntry(Entry):
    @cachedproperty
    def content(self):
        return self.find_existing_content(self.urn)

    @cachedproperty
    def article_context(self):
        article_name = self.content.uniqueId.replace('-image-group', '')
        return zeit.cms.interfaces.ICMSContent(article_name)

    def do_import(self):
        if not self.content:
            log.info('No existing image found for %s', self.urn)
            return
        self.update()
        self.publish(self.content)

    def update(self):
        if not self.has_changes(self.content):
            return
        log.info('Update %s', self.content)
        self.apply_to_cms()

    def apply_to_cms(self):
        with zeit.cms.checkout.helper.checked_out(self.article_context) as co:
            news = zeit.newsimport.news.Image(self.entry, co)
            image = news.do_import()
            if image is not None:
                co.main_image = co.main_image.create(image)

    def retract(self):
        if not self.content:
            return
        if zeit.cms.content.sources.FEATURE_TOGGLES.find('dpa_import_delete_image'):
            if self.article_context.main_image is not None:
                Image(self.entry, self.article_context).delete()


class Image(Entry):
    def __init__(self, entry, article):
        super().__init__(entry)
        self.article = article

    def do_import(self):
        if not self.metadata:
            return None
        return super().do_import()

    @cachedproperty
    def metadata(self):
        for item in self.entry['associations']:
            if item['type'] == 'image':
                try:
                    # Do we have to be this defensive?
                    item['renditions'][0]['url']
                    return item
                except (IndexError, KeyError):
                    pass
        log.info('No image available for %s', self.entry['urn'])
        return None

    @cachedproperty
    def image_url(self):
        return self.metadata['renditions'][0]['url']

    @cachedproperty
    def urn(self):
        return self.metadata['urn']

    @cachedproperty
    def date(self):
        return pendulum.parse(self.metadata['version_created'])

    @cachedproperty
    def dpa_version(self):
        return self.metadata['version']

    @cachedproperty
    def filename(self):
        return f'{self.article.__name__}-image-group'

    def construct_image_group(self, image_group=None):
        image = zeit.content.image.image.get_remote_image(self.image_url)
        if not image:
            log.warning(
                'Remote image %s unavailable for article %s.', self.image_url, self.entry['urn']
            )
            return None
        image.__name__ = f'image.{image.format.lower()}'
        if image_group is None:
            image_group = zeit.content.image.imagegroup.ImageGroup.from_image(
                self.folder, self.filename, image
            )
        self.apply_to_cms(image_group)
        image_group[image_group.master_image] = image
        return image_group

    def create(self):
        return self.construct_image_group()

    def apply_to_cms(self, image_group):
        with zeit.cms.checkout.helper.checked_out(image_group) as co:
            metadata = zeit.content.image.interfaces.IImageMetadata(co)
            metadata.title = self.metadata['headline']
            metadata.caption = self.metadata['caption']
            metadata.copyright = (None, 'Andere', self.metadata['creditline'], None, None)
            news_properties = zeit.newsimport.interfaces.IDPANews(co)
            news_properties.urn = self.metadata['urn']
            news_properties.version = self.metadata['version']
            # Same pubstatus as corresponding article
            news_properties.pubstatus = self.entry['pubstatus']

    def update(self, image_group):
        if not self.has_changes(image_group):
            return None
        log.info('Update %s for article %s', image_group, self.entry['urn'])
        return self.construct_image_group(image_group)

    def delete(self):
        try:
            image_group = zeit.cms.interfaces.ICMSContent(self.article.main_image.target)
            # NOTE: this line has no effect when testing against
            # IPublishInfo(image_group).published. But we decide to keep
            # it here:
            IPublish(image_group).retract(background=False)
            del self.article.__parent__[image_group.__name__]
            log.info(
                'Retracted and deleted article image %s for article %s',
                self.article.main_image.target,
                self.entry['urn'],
            )
        except Exception as error:
            log.error(
                'Error %s while retracting main image for %s with %s',
                repr(error),
                self.article.uniqueId,
                self.entry['urn'],
            )
            raise


@metrics.EXECUTION_TIME.time()
@metrics.COUNT_EXCEPTIONS.count_exceptions()
def process_task(entry, profile_name='weblines'):
    log.info('Process %s', entry['urn'])
    if log.isEnabledFor(logging.DEBUG):
        log.debug('Entry contents:\n' + json.dumps(entry, indent=2))

    news = Entry.from_entry(entry)
    if news.usable:
        try:
            content = news.do_import()
            metrics.COUNT_PUBLISH.inc()
        except Exception:
            log.error('Error while publishing %s', entry['urn'])
            metrics.COUNT_PUBLISH_ERROR.inc()
            raise
        if content is None:
            log.info('Skipped import of %s', entry['urn'])
        else:
            log.info('Published %s (as %s).', entry['urn'], content.uniqueId)
    else:
        try:
            content = news.retract()
            del content.__parent__[content.__name__]
            metrics.COUNT_RETRACT.inc()
        except Exception:
            log.error('Error while retracting %s', entry['urn'])
            metrics.COUNT_RETRACT_ERROR.inc()
            raise
        if content is None:
            log.info('Skipped retracting %s, not found in vivi', entry['urn'])
        else:
            log.info('Retracted %s (%s).', entry['urn'], content.uniqueId)

    dpa = zope.component.getUtility(zeit.newsimport.interfaces.IDPA, name=profile_name)
    DeleteFromQueueDataManager(dpa, entry['_wireq_receipt'], entry['urn'])


@zope.interface.implementer(ISavepointDataManager)
class DeleteFromQueueDataManager:
    def __init__(self, dpa, receipt, urn):
        transaction.get().join(self)
        self.dpa = dpa
        self.receipt = receipt
        # Only for diagnostics
        self.urn = urn

    def abort(self, transaction):
        pass

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_abort(self, transaction):
        pass

    def tpc_vote(self, transaction):
        response = self.dpa.delete_entry(self.receipt)
        if response.status_code == 204:
            log.info('Entry %s deleted from dpa API queue', self.urn)
        elif response.status_code == 410:
            log.info(
                'Entry %s with receipt %s returned %s', self.urn, self.receipt, response.status_code
            )
        else:
            log.error(
                'Entry %s with receipt %s returned %s', self.urn, self.receipt, response.status_code
            )

    def tpc_finish(self, transaction):
        pass

    def sortKey(self):
        # Try to sort last, so that we vote last.
        return '~zeit.newsimport:%f' % time()

    def savepoint(self):
        return NoOpSavepoint()

    def __repr__(self):
        return '<%s.%s for %s in %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.urn,
            transaction.get(),
        )


@zope.interface.implementer(IDataManagerSavepoint)
class NoOpSavepoint:
    def rollback(self):
        raise RuntimeError('Cannot rollback remote API savepoints.')
