import argparse
import importlib.resources
import logging
import os
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
        poll_interval = context.opts['poll_interval']

        db_is_current = _db_is_current(context)
        while not db_is_current:
            context.bind.rollback()
            time.sleep(poll_interval)
            db_is_current = _db_is_current(context)

        return ()

    config = alembic.config.Config(
        importlib.resources.files(__package__) / 'migrations/alembic.ini',
        ini_section='predeploy',
    )
    script = alembic.script.ScriptDirectory.from_config(config)
    with EnvironmentContext(
        config, script, fn=wait, dont_mutate=True, poll_interval=options.poll_interval
    ):
        script.run_env()


def _db_is_current(context):
    from alembic.script.revision import ResolutionError

    script = context.opts['script']
    head_revision = script.as_revision_number('heads') or ()
    db_revision = context.get_current_heads()
    # Like alembic.script.base._upgrade_revs, but readonly
    todo = script.iterate_revisions('head', db_revision, implicit_base=True)
    try:
        todo = len(list(todo))
    except ResolutionError:
        log.info(
            'Newest migration %s, DB version %s unknown, assumed newer',
            head_revision,
            db_revision,
        )
        return True

    wait = ', will wait %s' % context.opts.get('poll_interval') if todo else ''
    log.info(
        'Newest migration %s, DB version %s, %s steps remaining%s',
        head_revision,
        db_revision,
        todo,
        wait,
    )
    return not todo


def alembic():
    import alembic.config

    os.environ['ALEMBIC_CONFIG'] = str(
        importlib.resources.files(__package__) / 'migrations/alembic.ini'
    )
    alembic.config.main()
