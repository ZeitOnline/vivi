import argparse
import logging
import zope.app.appsetup.product
import zope.interface

import zeit.cms.cli
import zeit.sourcepoint.interfaces
import zeit.sourcepoint.javascript


log = logging.getLogger(__name__)


@zope.interface.implementer(zeit.sourcepoint.interfaces.IJavaScript)
def sourcepoint_from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.sourcepoint')
    return zeit.sourcepoint.javascript.JavaScript(
        config['sp-javascript-folder'],
        config['sp-url'],
        config['sp-api-token'],
        'msg')


@zeit.cms.cli.runner()
def update(principal=zeit.cms.cli.from_config(
        'zeit.sourcepoint', 'update-principal')):
    log.info('Checking Sourcepoint JS')
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript)
    store.update()


@zeit.cms.cli.runner()
def sweep():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    options = parser.parse_args()
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IJavaScript)
    store.sweep(keep=options.keep)
    log.info('Sweep end')


@zope.interface.implementer(zeit.sourcepoint.interfaces.IAdDefend)
def addefend_from_product_config():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.sourcepoint')
    return zeit.sourcepoint.javascript.JavaScript(
        config['addefend-javascript-folder'],
        config['addefend-url'],
        config['addefend-api-token'],
        'addefend_script')


@zeit.cms.cli.runner()
def update_addefend(principal=zeit.cms.cli.from_config(
        'zeit.sourcepoint', 'update-principal')):
    log.info('Checking AdDefend JS')
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IAdDefend)
    store.update()


@zeit.cms.cli.runner()
def sweep_addefend():
    log.info('Sweep start')
    parser = argparse.ArgumentParser()
    parser.add_argument('--keep', type=int, default=10)
    options = parser.parse_args()
    store = zope.component.getUtility(zeit.sourcepoint.interfaces.IAdDefend)
    store.sweep(keep=options.keep)
    log.info('Sweep end')
