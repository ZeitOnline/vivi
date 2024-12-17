import json
import logging

from google.cloud import storage
import grokcore.component as grok
import zope.interface

from zeit.cms.content.sources import FEATURE_TOGGLES
import zeit.workflow.interfaces

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
            context, zeit.workflow.interfaces.IPublisherData, name='datascience'
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
    if event.publishing or FEATURE_TOGGLES.find('disable_revisions_on_checkin'):
        return
    log.info('AfterCheckinEvent: Creating async revision job for %s', context.uniqueId)
    create_revision.apply_async((context.uniqueId,), countdown=5)


# XXX should we create our own queue?
@zeit.cms.celery.task(bind=True, queue='manual')
def create_revision(self, uniqueId):
    # XXX can we check if the checksum has changed and only fire event if true?
    content = zeit.cms.interfaces.ICMSContent(uniqueId, None)
    if content is None:
        log.warning('Could not resolve %s, ignoring.', uniqueId)
        return
    revision = zope.component.getUtility(IContentRevision)
    revision(content)
