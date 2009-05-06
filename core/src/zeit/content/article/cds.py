# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import gocept.filestore
import gocept.runner
import logging
import os.path
import zeit.cms.content.interfaces
import zeit.cms.content.interfaces
import zeit.cms.settings.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.article.interfaces
import zope.app.appsetup
import zope.app.component.hooks
import zope.component


log = logging.getLogger(__name__)


PRINCIPAL =  'zope.cds'


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
    log.debug('Start export to Content-Drehscheibe')
    if not object.export_cds:
        log.debug('Export flag is not set. Exiting.')
        return
    fs = get_cds_filestore('cds-export')
    if fs is None:
        log.debug('Filestore is not set. Exiting.')
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


def import_one():
    fs = get_cds_filestore('cds-import')
    files = sorted(fs.list('new'))
    if not files:
        return False

    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.article')
    valid_path = config['cds-import-valid-path'].split('/')
    invalid_path = config['cds-import-invalid-path'].split('/')

    path = files[0]
    filename = os.path.basename(path)
    with open(path, 'rb') as f:
        article = zeit.content.article.article.Article(f)

    article.updateDAVFromXML()
    zope.interface.alsoProvides(
        article,
        zeit.content.article.interfaces.ITagesspiegelArticle)
    zeit.cms.workflow.interfaces.IModified(article).last_modified_by = (
        PRINCIPAL)

    import_ = True
    container = None
    name = filename
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
                log.error(
                    'Error while importing %s: UUID already taken by %s' % (
                        filename, existing_article.uniqueId))
                import_ = False

    if import_ and container is None:
        site = zope.app.component.hooks.getSite()
        settings = zeit.cms.settings.interfaces.IGlobalSettings(site)
        prefix = (valid_path if article.ressort else invalid_path)
        container = settings.get_working_directory(prefix)
    if import_:
        container[name] = article

    fs.move(filename, 'new', 'cur')

    return True


def import_and_schedule():
    if import_one():
        return 0.02
    return 10


@gocept.runner.appmain(ticks=360, principal=PRINCIPAL)
def import_main():
    return import_and_schedule()
