from unittest import mock
import argparse
import logging

import transaction
import zope.component

from zeit.cms.workflow.interfaces import IManualPublicationOptions, IPublish, IPublishInfo
import zeit.cms.celery
import zeit.cms.cli


log = logging.getLogger(__name__)
IGNORE_SERVICES = ['airship', 'speechbert', 'summy']


@zeit.cms.celery.task(queue='manual')
def publish_content(options: dict):
    """This publish task is running inside a celery worker because
    we do not want to unregister and reregister the hooks for the application if this
    function is called inside the regular vivi process
    """
    options = IManualPublicationOptions(options)
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
    zeit.workflow.publish_3rdparty.PublisherData.ignore = (
        options.ignore_services.split(',') + IGNORE_SERVICES
    )

    for uid in options.unique_ids:
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
    parser.add_argument('--filename', '-f', help='filename with uniqueId per line')

    for name, field in zope.schema.getFields(IManualPublicationOptions).items():
        arg_name = f'--{name.replace("_", "-")}'
        if isinstance(field, zope.schema.Bool):
            parser.add_argument(arg_name, action='store_true', help=field.title)
        elif isinstance(field, zope.schema.TextLine):
            parser.add_argument(arg_name, help=field.title, default=field.default)
        elif isinstance(field, zope.schema.Text):
            parser.add_argument(arg_name, help=field.title, default=field.default)
        else:
            parser.add_argument(arg_name, help=field.title)

    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)

    to_publish = open(options.filename).read()

    options = options.__dict__
    options['unique_ids'] = to_publish

    publish_content.delay(options)


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
