import zope.component

import zeit.objectlog.generation


def update(root):
    site_manager = zope.component.getSiteManager()
    objectlog = site_manager['objectlog']._object_log
    for key in list(objectlog):  # production has ~90k, fits into ~200M
        value = objectlog[key]
        id = key.referenced_object
        for item in value.values():
            item.uniqueId = id
            del item.object_reference
        objectlog[id] = value
        del objectlog[key]


def evolve(context):
    zeit.objectlog.generation.do_evolve(context, update)
