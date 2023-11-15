import argparse
import grokcore.component as grok
import logging
import zope.interface

import zeit.cms.cli
import zeit.sourcepoint.interfaces
import zeit.sourcepoint.javascript


log = logging.getLogger(__name__)


@grok.implementer(zeit.sourcepoint.interfaces.IJavaScript)
def addefend_from_product_config():
    return zeit.sourcepoint.javascript.JavaScript.from_product_config('addefend')


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.sourcepoint', 'update-principal'))
def update():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str)
    options = parser.parse_args()
    log.info(f'Checking {options.source} JS')
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript, name=options.source)
    store.update()


@zeit.cms.cli.runner(principal=zeit.cms.cli.from_config('zeit.sourcepoint', 'update-principal'))
def sweep():
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    parser.add_argument('--source', type=str)
    options = parser.parse_args()
    log.info(f'Sweep {options.source} start')
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript, name=options.source)
    store.sweep(keep=options.keep)
    log.info(f'Sweep {options.source} end')
