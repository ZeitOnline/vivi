# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from __future__ import with_statement
import gocept.filestore
import gocept.runner
import logging
import os.path
import zeit.cms.content.interfaces
import zeit.cms.settings.interfaces
import zeit.cms.workflow.interfaces
import zeit.connector.interfaces
import zeit.content.article.interfaces
import zeit.content.article.interfaces
import zope.app.appsetup
import zope.app.component.hooks
import zope.component


log = logging.getLogger(__name__)


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
    path = files[0]
    name = os.path.basename(path)
    with open(path, 'rb') as f:
        article = zeit.content.article.article.Article(f)

    article.updateDAVFromXML()
    zope.interface.alsoProvides(
        article,
        zeit.content.article.interfaces.ITagesspiegelArticle)
    site = zope.app.component.hooks.getSite()
    settings = zeit.cms.settings.interfaces.IGlobalSettings(site)
    directory = settings.get_online_working_directory()
    directory[name] = article

    fs.move(name, 'new', 'cur')

    return True


def import_and_schedule():
    if import_one():
        return 0.02
    return 10


@gocept.runner.appmain(ticks=360, principal='zope.cds')
def import_main():
    return import_and_schedule()
