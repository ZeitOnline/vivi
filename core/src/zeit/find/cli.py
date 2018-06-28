from argparse import ArgumentParser
from datetime import datetime
from gocept.runner import once
from logging import getLogger
from operator import itemgetter
from pprint import pformat
from zeit.cms.interfaces import ICMSContent
from zeit.find import solr, elastic


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
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Report query & results')
    parser.add_argument(
        '-p', '--payload', action='store_true', help='Dump result payload')
    args = parser.parse_args()
    return args, dict(convert(args.conditions))


def perform_search(module, get_id):
    args, conditions = parse()
    query = module.query(**conditions)
    if args.verbose:
        log.info('using query: {}'.format(query))
    response = module.search(query, include_payload=args.payload)
    log.info('got {} results'.format(response.hits))
    if args.verbose:
        for idx, item in enumerate(response):
            info = '#{}: {}'.format(idx, get_id(item))
            if args.payload:
                info += '\n' + pformat(item)
            log.info(info)


@once(principal='zope.manager')
def search_solr():
    perform_search(solr, itemgetter('uniqueId'))


@once(principal='zope.manager')
def search_elastic():
    perform_search(elastic, lambda item: ICMSContent(item).uniqueId)
