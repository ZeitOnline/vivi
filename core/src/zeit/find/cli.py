from argparse import ArgumentParser
from gocept.runner import once
from zeit.find import search, elastic


def parse():
    parser = ArgumentParser(description='Elasticsearch debug client')
    parser.add_argument('-f', '--fulltext', help='Fulltext search term')
    parser.add_argument('-a', '--authors', help='Search author name')
    return vars(parser.parse_args())


@once(principal='zope.manager')
def search_solr():
    args = parse()
    query = search.query(**args)
    print('using query: {}'.format(query))
    response = search.search(query)
    print('got {} results'.format(len(response)))


@once(principal='zope.manager')
def search_elastic():
    args = parse()
    query = elastic.query(**args)
    print('using query: {}'.format(query))
    response = elastic.search(query)
    print('got {} results'.format(response.hits))
