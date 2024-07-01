import argparse
import importlib.resources
import logging
import time

import zope.event

import zeit.cms.cli
import zeit.connector.interfaces
import zeit.content.cp.cache


log = logging.getLogger(__name__)


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


def wait_for_migrations():
    from alembic.runtime.environment import EnvironmentContext
    import alembic.config
    import alembic.script

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=10,
        help='seconds to wait between polls',
    )
    options = parser.parse_args()

    # alembic loads config from ini file, then executes `env.py` (determined by
    # `script_location`), whose job it is to 1. establish the DB connection,
    # 2. call `run_migrations()`.
    # This in turn calls a worker function, which by default executes
    # migrations, but can be overridden by passing a custom function as `fn`.
    def wait(heads, context):
        head_revision = script.as_revision_number('heads') or ()
        db_is_current = False
        while not db_is_current:
            db_revision = context.get_current_heads()
            log.info('Newest migration %s, DB version %s', head_revision, db_revision)

            if db_revision == head_revision:
                break
            log.info('DB is not current, will wait %s', options.poll_interval)
            context.bind.rollback()
            time.sleep(options.poll_interval)
        return ()

    config = alembic.config.Config(
        importlib.resources.files(__package__) / 'migrations/alembic.ini',
        ini_section='predeploy',
    )
    script = alembic.script.ScriptDirectory.from_config(config)
    with EnvironmentContext(config, script, fn=wait, dont_mutate=True):
        script.run_env()
