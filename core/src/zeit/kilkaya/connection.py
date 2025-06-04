import argparse
import logging

import grokcore.component as grok
import zope.interface

import zeit.cms.cli
import zeit.kilkaya.interfaces
import zeit.kilkaya.json


log = logging.getLogger(__name__)


@grok.implementer(zeit.kilkaya.interfaces.IJson)
def teaser_splittests_from_product_config():
    return zeit.kilkaya.json.Json.from_product_config('teaser_splittests')


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.kilkaya', 'update-principal'))
def update():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str)
    options = parser.parse_args()
    log.info(f'Checking {options.source} JSON')
    store = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name=options.source)
    for _ in zeit.cms.cli.commit_with_retry():
        store.update()


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.kilkaya', 'update-principal'))
def sweep():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    parser.add_argument('--source', type=str)
    options = parser.parse_args()
    log.info(f'Sweep {options.source} start')
    store = zope.component.getUtility(zeit.kilkaya.interfaces.IJson, name=options.source)
    for _ in zeit.cms.cli.commit_with_retry():
        store.sweep(keep=options.keep)
    log.info(f'Sweep {options.source} end')
