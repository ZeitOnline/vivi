import argparse

import zeit.cms.cli
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
