import logging

import ZODB.POSException
import zope.component

import zeit.objectlog.generation


log = logging.getLogger(__name__)


def update(root):
    site_manager = zope.component.getSiteManager()
    objectlog = site_manager['objectlog']._object_log
    for key in list(objectlog):  # production has ~90k, fits into ~200M
        value = objectlog[key]
        id = key.referenced_object
        try:
            for item in value.values():
                item.uniqueId = id
                del item.object_reference
            objectlog[id] = value
        except ZODB.POSException.POSKeyError:
            log.warning('ZODB.POSException.POSKeyError, removing lost key %s', key)
        del objectlog[key]


def evolve(context):
    zeit.objectlog.generation.do_evolve(context, update)
