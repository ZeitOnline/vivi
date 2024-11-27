from unittest import mock
import argparse
import logging

import transaction
import zope.component

import zeit.cms.cli


log = logging.getLogger(__name__)
IGNORE_SERVICES = ['airship', 'speechbert']


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def publish():
    parser = argparse.ArgumentParser(description='Publish content')
    parser.add_argument('--filename', help='filename with uniqueId per line')
    parser.add_argument(
        '--force', '-f', action='store_true', help='Publish even if currently unpublished'
    )
    parser.add_argument('--skip-deps', action='store_true', help='Ignore publication dependencies')

    parser.add_argument(
        '--use-checkin-hooks',
        action='store_true',
        help='Notify webhooks after checkin, like contenthub',
    )

    parser.add_argument(
        '--use-publish-hooks',
        action='store_true',
        help='Notify webhooks after publish, like contenthub',
    )

    parser.add_argument(
        '--ignore-services',
        default=[],
        help=f'Ignore 3rd party services; default: {IGNORE_SERVICES} will be extended by yours;',
        nargs='+',
    )
    parser.add_argument(
        '--wait-tms', action='store_true', help='Have publisher wait for TMS before fastly purge'
    )
    parser.add_argument(
        '--skip-tms-enrich',
        action='store_true',
        help='Skip TMS enrich, e.g. checkin already happened',
    )
    parser.add_argument(
        '--dlps', action='store_true', help='Update date_last_published_semantic timestamp'
    )

    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)

    registry = zope.component.getGlobalSiteManager()

    # No option, since there is no usecase for re-activating old breaking news
    log.info('Deactivating breaking news banner')
    assert registry.unregisterHandler(zeit.push.workflow.send_push_on_publish)

    if not options.dlps:
        log.info('Deactivating date_last_published_semantic')
        assert registry.unregisterHandler(
            zeit.cms.workflow.modified.update_date_last_published_semantic
        )

    if options.skip_tms_enrich:
        log.info('Deactivating TMS enrich')

        assert registry.unregisterHandler(zeit.retresco.update.index_before_publish)

    if options.skip_deps:
        log.info('Deactivating publish dependencies')
        mock.patch(
            'zeit.cms.workflow.dependency.Dependencies._find_adapters', return_value=()
        ).start()

    if not options.use_checkin_hooks:
        log.info('Deactivating checkin hooks')
        assert registry.unregisterHandler(zeit.cms.checkout.webhook.notify_after_checkin)

    if not options.use_publish_hooks:
        log.info('Deactivating publish hooks')
        assert registry.unregisterHandler(zeit.cms.checkout.webhook.notify_after_publish)

    if not options.wait_tms:
        mock.patch(
            'zeit.workflow.publish_3rdparty.TMS.wait_for_index_update', return_value=False
        ).start()

    log.info('Ignoring services %s', options.ignore_services)
    zeit.workflow.publish_3rdparty.PublisherData.ignore = options.ignore_services + IGNORE_SERVICES

    for line in open(options.filename):
        id = line.strip()
        content = zeit.cms.interfaces.ICMSContent(id, None)
        if content is None:
            log.warn('Skipping %s, not found', id)
            continue

        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if not (info.published or options.force):
            log.info('Skipping %s, not published and no --force', id)
            continue

        try:
            zeit.cms.workflow.interfaces.IPublish(content).publish(background=False)
            transaction.commit()
        except Exception:
            transaction.abort()


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def retract():
    parser = argparse.ArgumentParser(description='Retact content')
    parser.add_argument('--filename', help='filename with uniqueId per line')
    parser.add_argument(
        '--force', '-f', action='store_true', help='Retract even if currently unpublished'
    )
    parser.add_argument(
        '--ignore-services',
        default=IGNORE_SERVICES,
        help=f'Ignore 3rd party services; default: {IGNORE_SERVICES}; use to overwrite',
        nargs='+',
    )

    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)

    log.info('Ignoring services %s', options.ignore_services)
    zeit.workflow.publish_3rdparty.PublisherData.ignore = options.ignore_services

    for line in open(options.filename):
        id = line.strip()
        content = zeit.cms.interfaces.ICMSContent(id, None)
        if content is None:
            log.warn('Skipping %s, not found', id)
            continue

        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if not (info.published or options.force):
            log.info('Skipping %s, not published and no --force', id)
            continue

        try:
            zeit.cms.workflow.interfaces.IPublish(content).retract(background=False)
            transaction.commit()
        except Exception:
            transaction.abort()
