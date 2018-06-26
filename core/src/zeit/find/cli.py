from argparse import ArgumentParser
from gocept.runner import once
from logging import getLogger
from operator import itemgetter
from zeit.cms.interfaces import ICMSContent
from zeit.find import search, elastic


log = getLogger(__name__)


def parse():
    parser = ArgumentParser(description='Elasticsearch debug client')
    parser.add_argument('conditions', nargs='+', help='Search conditions')
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Report query & results')
    args = parser.parse_args()
    conditions = dict([c.split(':', 1) for c in args.conditions])
    return args, conditions


def perform_search(module, get_id):
    args, conditions = parse()
    query = module.query(**conditions)
    if args.verbose:
        log.info('using query: {}'.format(query))
    response = module.search(query)
    log.info('got {} results'.format(response.hits))
    if args.verbose:
        for idx, item in enumerate(response):
            log.info('#{}: {}'.format(idx, get_id(item)))


@once(principal='zope.manager')
def search_solr():
    perform_search(search, itemgetter('uniqueId'))


@once(principal='zope.manager')
def search_elastic():
    perform_search(elastic, lambda item: ICMSContent(item).uniqueId)
