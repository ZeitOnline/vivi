import argparse
import logging
import pickle
import sys

import transaction
import zope.component

import zeit.objectlog.interfaces


log = logging.getLogger(__name__)


def dump(filename):
    sys.setrecursionlimit(5000)  # default is 1000
    objectlog = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    storage = objectlog._object_log
    data = list(storage.items())
    # skip = []
    # for i, item in enumerate(data):
    #     try:
    #         pickle.dumps(item)
    #     except Exception:
    #         print('WARN Skipping %s' % i)
    #         skip.append(i)
    skip = [6908, 6911, 9938]
    for i in skip:
        del data[i]
    pickle.dump(data, open(filename, 'w'))


def load(filename):
    # XXX Empirically, this *has* to be latin-1 for py3 to be able to read py2
    # pickles, but no idea why.
    dumped = pickle.load(open(filename, 'rb'), encoding='latin-1')
    objectlog = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    storage = objectlog._object_log
    for key, value in dumped:
        if key not in storage:
            log.info('Setting %s', key.referenced_object)
            storage[key] = value
        else:
            log.info('Updating %s', key.referenced_object)
            current = storage[key]
            current.update(value)
        transaction.commit()


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def export_import():
    parser = argparse.ArgumentParser(description='Load or dump objectlog')
    parser.add_argument('action', choices=['load', 'dump'])
    parser.add_argument('filename')
    options = parser.parse_args()

    if options.action == 'dump':
        dump(options.filename)
    elif options.action == 'load':
        load(options.filename)
