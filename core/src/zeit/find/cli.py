from argparse import ArgumentParser
from datetime import datetime
from logging import getLogger
from pprint import pformat

from zeit.cms.interfaces import ICMSContent
import zeit.cms.cli
import zeit.find.search


log = getLogger(__name__)


def convert(conditions):
    for condition in conditions:
        name, value = condition.split(':', 1)
        if name in ('from_', 'until'):
            value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        yield name, value


def parse():
    parser = ArgumentParser(description='Elasticsearch debug client')
    parser.add_argument('conditions', nargs='+', help='Search conditions')
    parser.add_argument('-v', '--verbose', action='store_true', help='Report query & results')
    parser.add_argument('-p', '--payload', action='store_true', help='Dump result payload')
    args = parser.parse_args()
    return args, dict(convert(args.conditions))


@zeit.cms.cli.runner(principal='zope.manager')
def search_elastic():
    args, conditions = parse()
    query = zeit.find.search.query(**conditions)
    if args.verbose:
        log.info('using query: {}'.format(query))
    response = zeit.find.search.search(query, include_payload=args.payload)
    log.info('got {} results'.format(response.hits))
    if args.verbose:
        for idx, item in enumerate(response):
            info = '#{}: {}'.format(idx, ICMSContent(item).uniqueId)
            if args.payload:
                info += '\n' + pformat(item)
            log.info(info)
