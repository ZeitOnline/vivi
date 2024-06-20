import argparse

import zope.event

import zeit.cms.cli
import zeit.connector.interfaces
import zeit.content.cp.cache


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def prewarm_cache():
    parser = argparse.ArgumentParser(description='Prewarm cache')
    parser.add_argument('--filename', help='filename with uniqueId per line')
    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)
    for line in open(options.filename):
        id = line.strip()
        for _ in zeit.cms.cli.commit_with_retry():
            zeit.content.cp.cache.prewarm_cache(id)


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def refresh_cache():
    parser = argparse.ArgumentParser(description='Refresh cache')
    parser.add_argument('--filename', help='filename with uniqueId per line')
    options = parser.parse_args()
    if not options.filename:
        parser.print_help()
        raise SystemExit(1)
    for line in open(options.filename):
        id = line.strip()
        for _ in zeit.cms.cli.commit_with_retry():
            zope.event.notify(zeit.connector.interfaces.ResourceInvalidatedEvent(id))
