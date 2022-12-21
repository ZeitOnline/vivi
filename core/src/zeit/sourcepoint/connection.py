import argparse
import grokcore.component as grok
import logging
import zope.interface

import zeit.cms.cli
import zeit.sourcepoint.interfaces
import zeit.sourcepoint.javascript


log = logging.getLogger(__name__)


@grok.implementer(zeit.sourcepoint.interfaces.IJavaScript)
def sourcepoint_from_product_config():
    return zeit.sourcepoint.javascript.JavaScript.from_product_config(
        'sourcepoint')


@grok.implementer(zeit.sourcepoint.interfaces.IJavaScript)
def addefend_from_product_config():
    return zeit.sourcepoint.javascript.JavaScript.from_product_config(
        'addefend')


@zeit.cms.cli.runner()
def update(principal=zeit.cms.cli.from_config(
        'zeit.sourcepoint', 'update-principal')):
    log.info('Checking Sourcepoint JS')
    store = zope.component.getUtility(
        zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
    store.update()


@zeit.cms.cli.runner()
def sweep():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    options = parser.parse_args()
    store = zope.component.getUtility(
        zeit.sourcepoint.interfaces.IJavaScript, name='sourcepoint')
    store.sweep(keep=options.keep)
    log.info('Sweep end')


@zeit.cms.cli.runner()
def update_addefend(principal=zeit.cms.cli.from_config(
        'zeit.sourcepoint', 'update-principal')):
    log.info('Checking AdDefend JS')
    store = zope.component.getUtility(
        zeit.sourcepoint.interfaces.IJavaScript, name='addefend')
    store.update()


@zeit.cms.cli.runner()
def sweep_addefend():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    options = parser.parse_args()
    store = zope.component.getUtility(
        zeit.sourcepoint.interfaces.IJavaScript, name='addefend')
    store.sweep(keep=options.keep)
    log.info('Sweep end')
