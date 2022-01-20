import ast
import logging.config
import re


def configure(config):
    """Calls logging.config.dictConfig(), after transforming the input dictionary
    from a flat list of keys with dotted names into nested dicts (with some
    small added syntactic sugar). Example input:

    root.level: INFO
    # comma-separated handlers are converted to list
    root.handlers: console, other
    # Underscores in the key are translated to package dots
    # (since we reserve dots for nesting dicts)
    loggers.zope_interface.level: WARNING
    handlers.console.class: logging.StreamHandler
    handlers.console.formatter: console
    handlers.console.stream: ext://sys.stdout
    # In formatters, `class` is translated to `()` (so it's analoguous to
    # handlers, unclear why the stdlib has this inconsistency)
    formatters.console.class: zope.exceptions.log.Formatter
    formatters.console.format: %(asctime)s %(levelname) [%(name)s] %(message)s
    # Use __literal__ in key to express int/list/dict
    handlers.fluent.port__literal__ = 12345

    If not set, we add `disable_existing_loggers: False`. I don't think there's
    ever a usecase where True would make sense, since other packages will
    already have been imported before we run, and thus have loggers which would
    wrongly be silenced by it.
    """

    config = convert_dotted_keys_to_nested_dicts(config)
    apply_logging_syntax_fixes(config)
    capture = config.pop('capture_warnings', False)
    logging.config.dictConfig(config)
    logging.captureWarnings(capture)


def convert_dotted_keys_to_nested_dicts(mapping):
    result = {}
    for key, value in mapping.items():
        parent = result
        parts = key.split('.')
        for i, subkey in enumerate(parts):
            if i == len(parts) - 1:
                if '__literal__' in subkey:
                    subkey = subkey.replace('__literal__', '')
                    value = ast.literal_eval(value)
                parent[subkey] = value
            else:
                parent = parent.setdefault(subkey, {})
    return result


def apply_logging_syntax_fixes(config):
    config['version'] = 1
    config.setdefault('disable_existing_loggers', False)

    if config.get('root', {}).get('handlers'):
        config['root']['handlers'] = re.split(
            ', *', config['root']['handlers'])

    if 'loggers' in config:
        for key, value in list(config['loggers'].items()):
            if value.get('handlers'):
                value['handlers'] = re.split(', *', value['handlers'])
            dotted = key.replace('_', '.')
            if key != dotted:
                config['loggers'][dotted] = value
                del config['loggers'][key]

    if 'formatters' in config:
        for item in config['formatters'].values():
            if 'class' in item:
                item['()'] = item['class']
                del item['class']
