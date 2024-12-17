import json
import logging

from google.cloud import storage
import grokcore.component as grok
import zope.component
import zope.interface

from zeit.cms.content.sources import FEATURE_TOGGLES
from zeit.cms.interfaces import CONFIG_CACHE
from zeit.workflow.interfaces import IPublisherData
import zeit.cms.checkout.webhook
import zeit.content.article.interfaces
import zeit.content.cp.interfaces

from .interfaces import IContentRevision


log = logging.getLogger(__name__)


@zope.interface.implementer(IContentRevision)
class ContentRevision:
    def __init__(self, storage_project, storage_bucket):
        self.gcs_client = storage.Client(project=storage_project)
        self.bucket = self.gcs_client.bucket(storage_bucket)

    @classmethod
    @zope.interface.implementer(IContentRevision)
    def factory(cls):
        config = zeit.cms.config.package('zeit.revisions')
        return cls(config['storage-project'], config['storage-bucket'])

    def __call__(self, context):
        content = zope.component.getAdapter(
            context, IPublisherData, name='datascience'
        ).publish_json()
        uuid = zeit.cms.content.interfaces.IUUID(context).shortened
        with zeit.cms.tracing.use_span(
            __name__ + '.tracing',
            'gcs',
            attributes={'db.operation': 'upload', 'id': uuid},
        ):
            self.upload_to_bucket(
                uuid,
                'application/json',
                json.dumps(content['properties']),
            )
            self.upload_to_bucket(uuid, 'text/xml', content['body'])

    def upload_to_bucket(self, uuid, content_type, payload):
        file_type = 'xml' if content_type == 'text/xml' else 'json'
        blob = self.bucket.blob(f'{uuid}.{file_type}')
        blob.upload_from_string(payload, content_type=content_type)


factory = ContentRevision.factory


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def create_revision_after_checkin(context, event):
    if (
        event.publishing
        or FEATURE_TOGGLES.find('disable_revisions_on_checkin')
        or zope.component.queryAdapter(context, IPublisherData, name='datascience') is None
    ):
        return
    filter = FILTERS.factory.getValues()
    if filter(context):
        log.info('AfterCheckinEvent: Creating async revision job for %s', context.uniqueId)
        create_revision.apply_async((context.uniqueId,), countdown=5)


@zeit.cms.celery.task(bind=True, queue='revisions')
def create_revision(self, uniqueId):
    content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if content is None:
        log.warning('Could not resolve %s, ignoring.', uniqueId)
        return
    revision = zope.component.getUtility(IContentRevision)
    revision(content)


class Filter(zeit.cms.checkout.webhook.Hook):
    def __init__(self):
        super().__init__('not-required', 'not-required')

    def __call__(self, content):
        return self.matches_criteria(content)


class FilterSource(zeit.cms.content.sources.SimpleXMLSource):
    config_url = 'checkin-revisions-config'
    default_filename = 'checkin-revisions.xml'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        filter = Filter()
        tree = self._get_tree()
        for node in tree.iterchildren('filter'):
            for include in node.xpath('include/*'):
                filter.add_include(include.tag, include.text)
            for exclude in node.xpath('exclude/*'):
                filter.add_exclude(exclude.tag, exclude.text)
        return filter

    def getValues(self):
        return self._values()


FILTERS = FilterSource()
