from argparse import ArgumentParser
import functools
import logging
import socket
import sys

from zope.security.management import getInteraction
import transaction
import zope.component

import zeit.cms.cli
import zeit.newsimport.interfaces
import zeit.newsimport.news


log = logging.getLogger(__name__)


def import_dpa_news_api(args=None):
    if args is None:
        args = sys.argv[1:]
    if len(args) >= 1 and args[0].endswith('.ini'):  # See zeit.cms.cli.runner
        args = args[1:]
    parser = ArgumentParser(description='Import DPA news article')
    arg = parser.add_argument
    arg(
        '-i',
        '--interval',
        type=int,
        default=0,
        help='seconds to wait between imports (0=exit after one run)',
    )
    arg('-o', '--owner', default='zope.dpa', help='article owner')
    arg('--profile', default='weblines', help='dpa API profile')
    args = parser.parse_args(args)

    @transaction_per_item
    def importer():
        getInteraction().participations[0]._zeit_connector_referrer = (
            'http://%s/runner/import_dpa_news' % socket.getfqdn()
        )
        dpa = zope.component.getUtility(zeit.newsimport.interfaces.IDPA, name=args.profile)
        entries = dpa.get_entries()
        log.info('%s entries received from dpa', len(entries))

        for entry in entries:
            process = functools.partial(zeit.newsimport.news.process_task, entry, args.profile)
            yield process

    run = zeit.cms.cli.runner(ticks=args.interval, principal=args.owner, once=False)(importer)
    return run()


def transaction_per_item(func):
    def wrapped():
        for action in func():
            try:
                action()
            except Exception as e:
                log.error('Error in item %s: %s', action, e, exc_info=True)
                transaction.abort()
            else:
                try:
                    transaction.commit()
                except transaction.interfaces.TransientError:
                    log.warning('Conflict error', exc_info=True)
                    transaction.abort()

    return wrapped
