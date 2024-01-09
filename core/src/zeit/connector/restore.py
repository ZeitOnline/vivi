import argparse
import logging
import sys

import zeit.connector.connector
import zeit.connector.filesystem
import zeit.connector.interfaces


log = logging.getLogger(__name__)


def set_props_from_file(argv=None):
    parser = argparse.ArgumentParser(description='Set DAV properties from Filesystem data')
    parser.add_argument(
        'uniqueId', help='uniqueId, prefix either http://xml.zeit.de or /var/cms/work'
    )
    parser.add_argument(
        '--dav-url', help='DAV URL', default='http://cms-backend.zeit.de:9000/cms/work/'
    )
    parser.add_argument('--fs-path', help='Filesystem path', default='/var/cms/work')
    parser.add_argument('--verbose', '-v', help='Increase verbosity', action='store_true')
    options = parser.parse_args(argv)
    setup_logging(logging.INFO if not options.verbose else logging.DEBUG)

    if not options.dav_url.endswith('/'):
        options.dav_url += '/'
    if options.fs_path.endswith('/'):
        options.fs_path = options.fs_path[:-1]
    if options.uniqueId.startswith('/var/cms/work'):
        options.uniqueId = options.uniqueId.replace('/var/cms/work', 'http://xml.zeit.de', 1)

    log.info('Processing %s', options.uniqueId)
    dav = zeit.connector.connector.Connector({'default': options.dav_url})
    fs = zeit.connector.filesystem.Connector(options.fs_path)
    # Cannot use Connector.changeProperties, since that excludes the `UUID`
    # property, and is too slow due to locking and id-canonicalizing.
    davres = dav._get_dav_resource(options.uniqueId)
    davres.change_properties(
        fs._get_properties(options.uniqueId), delmark=zeit.connector.interfaces.DeleteProperty
    )


def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-5.5s %(name)s %(message)s'))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)
