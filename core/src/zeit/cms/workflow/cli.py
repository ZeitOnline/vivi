from unittest import mock
import argparse
import logging

import transaction
import zope.component

import zeit.cms.cli
import zeit.connector.interfaces
import zeit.workflow
import zeit.workflow.interfaces
import zeit.workflow.publish


log = logging.getLogger(__name__)
IGNORE_SERVICES = ['airship', 'speechbert', 'summy']


def _publisher_payload(content, action, services):
    uuid = zeit.cms.content.interfaces.IUUID(content)
    result = {'uuid': uuid.shortened, 'uniqueId': content.uniqueId}
    for name, adapter in zope.component.getAdapters(
        (content,), zeit.workflow.interfaces.IPublisherData
    ):
        if not name or name not in services:
            continue
        data = getattr(adapter, f'{action}_json')()
        if data is not None:
            result[name] = data
    return result


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def tasks():
    parser = argparse.ArgumentParser(description='Publish/Retract by services')
    parser.add_argument('--filename', '-f', help='filename with uniqueId per line')
    parser.add_argument('--action', choices=['publish', 'retract'], default='publish')
    parser.add_argument('--services', help='Publish services', nargs='+', required=True)

    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)

    log.info(f'Run {options.action} {", ".join(options.services)} services')

    tasks = []
    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)
    for line in open(options.filename):
        id = line.strip()
        connector.invalidate_cache(id)
        content = zeit.cms.interfaces.ICMSContent(id, None)
        if content is None:
            log.warning('Skipping %s, not found', id)
            continue

        payload = _publisher_payload(content, options.action, options.services)
        action = 'update' if options.action == 'publish' else options.action
        payload = {
            k if k in ('uniqueId', 'uuid') else f'{action}_{k}': v for k, v in payload.items()
        }
        tasks.append(payload)

    publisher = zope.component.getUtility(zeit.cms.workflow.interfaces.IPublisher)
    publisher.request(tasks, 'tasks')


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def publish():
    parser = argparse.ArgumentParser(description='Publish content')
    parser.add_argument('--filename', '-f', help='filename with uniqueId per line')
    parser.add_argument(
        '--force-unpublished', action='store_true', help='Publish even if currently unpublished'
    )
    parser.add_argument(
        '--force-changed', action='store_true', help='Publish even if with semantic change'
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
        mock.patch('zeit.workflow.publish_3rdparty.TMS.wait_for_index_update', new=False).start()

    zeit.workflow.publish_3rdparty.PublisherData.ignore = options.ignore_services + IGNORE_SERVICES
    log.info('Ignoring services %s', zeit.workflow.publish_3rdparty.PublisherData.ignore)

    connector = zope.component.getUtility(zeit.connector.interfaces.IConnector)

    for line in open(options.filename):
        id = line.strip()
        connector.invalidate_cache(id)
        content = zeit.cms.interfaces.ICMSContent(id, None)
        if content is None:
            log.warning('Skipping %s, not found', id)
            continue

        info = zeit.cms.workflow.interfaces.IPublishInfo(content)
        if not (info.published or options.force_unpublished):
            log.info('Skipping %s, not published and no --force-unpublished', id)
            continue
        semantic = zeit.cms.content.interfaces.ISemanticChange(content)
        if (
            info.date_last_published is not None
            and semantic.last_semantic_change is not None
            and semantic.last_semantic_change > info.date_last_published
            and not options.force_changed
        ):
            log.info('Skipping %s, has semantic change and no --force-changed', id)
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

    zeit.workflow.publish_3rdparty.PublisherData.ignore = options.ignore_services
    log.info('Ignoring services %s', zeit.workflow.publish_3rdparty.PublisherData.ignore)

    for line in open(options.filename):
        id = line.strip()
        content = zeit.cms.interfaces.ICMSContent(id, None)
        if content is None:
            log.warning('Skipping %s, not found', id)
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
