# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import datetime
import gocept.filestore
import gocept.runner
import logging
import lovely.remotetask.interfaces
import lxml.etree
import os.path
import pytz
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.settings.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zope.app.appsetup
import zope.app.component.hooks
import zope.component
import zope.container.interfaces


log = logging.getLogger(__name__)


PRINCIPAL =  'zope.cds'
DELETE_TIMEOUT = datetime.timedelta(days=2)


class RemoveIfNotPublishedTask(object):

    zope.interface.implements(lovely.remotetask.interfaces.ITask)

    def __call__(self, service, jobid, input):
        article = zeit.cms.interfaces.ICMSContent(input, None)
        if article is None:
            # Was already deleted or moved. Do nothing.
            return
        if zeit.cms.workflow.interfaces.IPublishInfo(article).published:
            # The article was published. Do nothing.
            return
        log.info("Removing %s because it was not published after %s" % (
                 input, DELETE_TIMEOUT))
        del article.__parent__[article.__name__]


def get_cds_filestore(name):
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.article')
    store_dir = config.get(name)
    log.debug('Filestore is set to %s.' % store_dir)
    if store_dir is None:
        return None
    result = gocept.filestore.FileStore(store_dir)
    result.prepare()
    return result


@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def export(object, event):
    if object != event.master:
        # Only export master
        return
    log.debug('Start export to Content-Drehscheibe')
    wf = zeit.content.article.interfaces.ICDSWorkflow(object, None)
    if wf is None:
        return
    if not wf.export_cds:
        log.debug('Export flag is not set. Exiting.')
        return
    fs = get_cds_filestore('cds-export')
    if fs is None:
        log.error('Filestore is not set. Exiting.')
        return
    uuid = zeit.cms.content.interfaces.IUUID(object).id
    filename = '%s.xml' % uuid
    log.info('Exporting %s to Content-Drehscheibe.' % filename)
    f = fs.create(filename)
    data = zeit.connector.interfaces.IResource(object)
    f.write(data.data.read())
    f.close()
    fs.move(filename, 'tmp', 'new')
    log.debug('File %s was created. Leaving.' % filename)


def get_replacements(article):
    now = datetime.datetime.now(pytz.UTC)
    return dict(
        real_year='%04d' % now.year,
        real_month='%02d' % now.month,
        real_day='%02d' % now.day,
        ressort=article.ressort.lower() if article.ressort else u'',
        sub_ressort=(
            article.sub_ressort.lower() if article.sub_ressort else u''),
    )

def import_file(path):
    """Import single file from CDS."""
    log.info("Importing %s" % path)
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.article')
    valid_path = config['cds-import-valid-path']
    invalid_path = config['cds-import-invalid-path']
    with open(path, 'rb') as f:
        try:
            article = zeit.content.article.article.Article(f)
        except lxml.etree.XMLSyntaxError, e:
            log.error('Error while importing %s: %s (%s)' % (
                      path, type(e).__name__, e))
            return

    article.updateDAVFromXML()
    zope.interface.alsoProvides(
        article,
        zeit.content.article.interfaces.ITagesspiegelArticle)
    zeit.cms.workflow.interfaces.IModified(article).last_modified_by = (
        PRINCIPAL)

    container = None
    name = os.path.basename(path)
    uuid = zeit.cms.content.interfaces.IUUID(article)
    if uuid.id:
        existing_article = zeit.cms.interfaces.ICMSContent(uuid, None)
        if existing_article is not None:
            if zeit.cms.workflow.interfaces.IModified(
                existing_article).last_modified_by == PRINCIPAL:
                log.info('Overwriting unchanged %s with new version.' %
                         existing_article.uniqueId)
                container = existing_article.__parent__
                name = existing_article.__name__
                del container[name]
            else:
                log.warning(
                    'While importing %s: UUID already taken by %s' % (
                        path, existing_article.uniqueId))
                return

    if container is None:
        site = zope.app.component.hooks.getSite()
        settings = zeit.cms.settings.interfaces.IGlobalSettings(site)
        source = zeit.content.article.interfaces.IArticle['ressort'].source
        prefix = (valid_path if article.ressort in source else invalid_path)
        container = settings.get_working_directory(prefix,
                                                   **get_replacements(article))

    name = zope.container.interfaces.INameChooser(container).chooseName(
        name, article)
    container[name] = article
    article = container[name]

    # Disable automatic export to CDS.
    zeit.content.article.interfaces.ICDSWorkflow(article).export_cds = False

    # Create removal job
    tasks = zope.component.getUtility(
        lovely.remotetask.interfaces.ITaskService, 'general')
    # Compute delete timeout which is > DELETE_TIMEOUT but in the night
    now = datetime.datetime.now(pytz.UTC)
    remove_at = now + DELETE_TIMEOUT + datetime.timedelta(days=1)
    remove_at = remove_at.replace(hour=1)
    remove_in = remove_at - datetime.datetime.now(pytz.UTC)
    delay = 60*60*24 * remove_in.days + remove_in.seconds
    tasks.addCronJob(
        u'zeit.content.article.cds.remove_if_not_published',
        article.uniqueId, delay=delay)



def import_one():
    fs = get_cds_filestore('cds-import')
    files = sorted(fs.list('new'))
    if not files:
        return False
    path = files[0]
    import_file(path)
    fs.move(os.path.basename(path), 'new', 'cur')
    return True




def import_and_schedule():
    if import_one():
        return 10
    return 60


@gocept.runner.appmain(ticks=360, principal=PRINCIPAL)
def import_main():
    return import_and_schedule()


class CDSWorkflow(object):
    """Workflow extension for the CDS."""

    zope.interface.implements(zeit.content.article.interfaces.ICDSWorkflow)
    zope.component.adapts(zeit.content.article.interfaces.IArticle)

    zeit.cms.content.dav.mapProperties(
        zeit.content.article.interfaces.ICDSWorkflow,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('export_cds',),
        live=True)

    def __init__(self, context):
        self.context = context
        if self.export_cds is None:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                self.context)
            if metadata.product and metadata.product.id == 'ZEDE':
                self.export_cds = True


@zope.component.adapter(CDSWorkflow)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def cdsworkflow_properties(context):
    return zeit.connector.interfaces.IWebDAVProperties(context.context)
