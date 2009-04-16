# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.app.appsetup
import gocept.filestore
import zope.component
import zeit.content.article.interfaces
import zeit.cms.workflow.interfaces
import zeit.cms.content.interfaces
import zeit.connector.interfaces

def get_cds_filestore():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.content.article') 
    store_dir = config.get('cds_filestore')
    if store_dir is None:
        return None
    result = gocept.filestore.FileStore(store_dir)
    result.prepare()
    return result

@zope.component.adapter(
    zeit.content.article.interfaces.IArticle,
    zeit.cms.workflow.interfaces.IPublishedEvent)
def export(object, event):
    if not object.export_cds:
        return
    fs = get_cds_filestore()
    if fs is None:
        return
    uuid = zeit.cms.content.interfaces.IUUID(object).id
    filename = '%s.xml' % uuid
    f = fs.create(filename)
    data = zeit.connector.interfaces.IResource(object)
    f.write(data.data.read())
    f.close()
    fs.move(filename, 'tmp', 'new')
