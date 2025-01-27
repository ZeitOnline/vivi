from unittest import mock
import argparse
import contextlib
import logging

import transaction
import zope.component

from zeit.cms.workflow.interfaces import (
    IManualPublicationOptions,
    IPublicationDependencies,
    IPublish,
    IPublishInfo,
)
from zeit.cms.workflow.options import PublicationOptions
import zeit.cms.celery
import zeit.cms.cli


log = logging.getLogger(__name__)
IGNORE_SERVICES = ['airship', 'speechbert', 'summy']


@contextlib.contextmanager
def temporary_unregister_handlers(registry, handlers):
    try:
        for handler in handlers:
            assert registry.unregisterHandler(handler)
        yield
    finally:
        for handler in handlers:
            registry.registerHandler(handler)


@contextlib.contextmanager
def temporary_unregister_adapters(registry, adapters):
    # registry.adapters._adapters[1][zeit.content.article.interfaces.IArticle]
    try:
        for provided, name in adapters:
            adapter = registry.queryAdapter(None, provided, name)
            if adapter is not None:
                registry.unregisterAdapter(adapter, None, provided, name)
        yield
    finally:
        for required, provided, name in adapters:
            adapter = registry.queryAdapter(required, provided, name)
            if adapter is not None:
                registry.registerAdapter(adapter, required, provided, name)


@zeit.cms.celery.task(queue='manual')
def publish_content(options: IManualPublicationOptions):
    """This publish task is running inside a celery worker because
    we do not want to unregister and reregister the hooks for the application if this
    function is called inside the regular vivi process
    """
    registry = zope.component.getGlobalSiteManager()
    handlers_to_unregister = []
    adapters_to_unregister = []

    # No option, since there is no usecase for re-activating old breaking news
    log.info('Deactivating breaking news banner')
    handlers_to_unregister.append(zeit.push.workflow.send_breaking_news_banner)

    if not options.dlps:
        log.info('Deactivating date_last_published_semantic')
        handlers_to_unregister.append(
            zeit.cms.workflow.modified.update_date_last_published_semantic
        )

    if options.skip_tms_enrich:
        log.info('Deactivating TMS enrich')
        handlers_to_unregister.append(zeit.retresco.update.index_before_publish)

    if options.skip_deps:
        log.info('Deactivating publish dependencies')
        adapters_to_unregister.append((IPublicationDependencies, ''))

    if not options.use_checkin_hooks:
        log.info('Deactivating checkin hooks')
        handlers_to_unregister.append(zeit.cms.checkout.webhook.notify_after_checkin)

    if not options.use_publish_hooks:
        log.info('Deactivating publish hooks')
        handlers_to_unregister.append(zeit.cms.checkout.webhook.notify_after_publish)

    if not options.wait_tms:
        mock.patch(
            'zeit.workflow.publish_3rdparty.TMS.wait_for_index_update', return_value=False
        ).start()

    log.info('Ignoring services %s', options.ignore_services)
    for service in options.ignore_services:
        adapters_to_unregister.append((zeit.workflow.interfaces.IPublisherData, service))

    with (
        temporary_unregister_handlers(registry, handlers_to_unregister),
        temporary_unregister_adapters(registry, adapters_to_unregister),
    ):
        for line in options.filename.decode('utf-8').splitlines():
            uid = line.strip()
            content = zeit.cms.interfaces.ICMSContent(uid, None)
            if content is None:
                log.warn('Skipping %s, not found', uid)
                continue

            info = IPublishInfo(content)
            if not (info.published or options.force_unpublished):
                log.info('Skipping %s, not published and no --force-unpublished', uid)
                continue
            semantic = zeit.cms.content.interfaces.ISemanticChange(content)
            if (
                info.date_last_published is not None
                and semantic.last_semantic_change is not None
                and semantic.last_semantic_change > info.date_last_published
                and not options.force_changed
            ):
                log.info('Skipping %s, has semantic change and no --force-changed', uid)
                continue

            try:
                IPublish(content).publish(background=False)
                transaction.commit()
            except Exception:
                transaction.abort()


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def publish():
    parser = argparse.ArgumentParser(description='Publish content')

    for name, field in zope.schema.getFields(IManualPublicationOptions).items():
        arg_name = f'--{name.replace("_", "-")}'
        if isinstance(field, zope.schema.Bool):
            parser.add_argument(arg_name, action='store_true', help=field.title)
        elif isinstance(field, zope.schema.List):
            parser.add_argument(arg_name, help=field.title, default=field.default, nargs='+')
        elif isinstance(field, zope.schema.Bytes):
            parser.add_argument(arg_name, type=lambda x: open(x, 'rb').read(), help=field.title)
        else:
            parser.add_argument(arg_name, help=field.title, default=field.default)

    options = parser.parse_args()
    publish_content(PublicationOptions(**options.__dict__))


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

        info = IPublishInfo(content)
        if not (info.published or options.force):
            log.info('Skipping %s, not published and no --force', id)
            continue

        try:
            IPublish(content).retract(background=False)
            transaction.commit()
        except Exception:
            transaction.abort()
