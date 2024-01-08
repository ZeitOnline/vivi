import logging

import paste.deploy.loadwsgi


log = logging.getLogger(__name__)


def wsgi_pipeline(app, pipeline, settings):
    """Wraps the given WSGI `app` in a filter pipeline.

    This is an alternative to defining the pipeline in a paste.ini file.
    Instead of describing the pipeline like this::

        [pipeline:main]
        one
        two
        app
        [application:app]
        use = egg:my.package#main
        config_for_app = foo
        [filter:one]
        use = egg:some.package#filter
        config1 = bar
        [filter:two]
        use = call:some.module:function
        config2 = qux

    This function enables doing something like::

        [application:main]
        use = egg:my.package#main
        config_for_app = foo
        one.config1 = bar
        two.config2 = qux

        def wsgi_app(global_conf, **local_conf):
            app = ...
            wsgi_pipeline(app, [
                ('one', 'egg:some.package#filter'),
                ('two', 'call:some.module:function'),
            ], local_conf)

    This also allows for getting the settings for all pipeline stages from e.g.
    environment variables (or anywhere, really), instead of the paste.ini file,
    without requiring any support for this from the stages themselves.

    Ingress is thought to be at the start, and the app after the end of the
    `pipeline` list. Items in that list are tuples with name and entrypoint;
    entrypoint can be either 'egg:some.package#entrypoint' (must be of type
    `paste.filter_app_factory`) or 'call:some.module:function' (must have
    signature `(app, global_conf, **local_conf)`).

    `settings` is a dict; to support configuring all pipeline stages from a
    single settings dict, keys can be dotted names ('prefix.key = value'). All
    keys whose prefix matches the `name` entry in the `pipeline` list will be
    passed to that pipeline stage (with the prefix removed).

    """
    for item in reversed(pipeline):
        name, factory = item
        loader = paste.deploy.loadwsgi.loadcontext(paste.deploy.loadwsgi.FILTER, factory)
        if factory.startswith('call'):
            loader.protocol = 'paste.filter_app_factory'
        prefix = name + '.'
        loader.local_conf = {
            key.replace(prefix, '', 1): value
            for key, value in settings.items()
            if key.startswith(prefix)
        }
        try:
            app = loader.create()(app)
        except Exception:
            log.error('Could not load pipeline stage %r', name)
            raise

    return app
