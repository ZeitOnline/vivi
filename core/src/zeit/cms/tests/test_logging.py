import unittest
import zeit.cms.logging


class LoggingConfigTest(unittest.TestCase):
    def test_convert_dotted_keys_to_nested_dicts(self):
        convert = zeit.cms.logging.convert_dotted_keys_to_nested_dicts
        config = {
            'one.a.a1': 'leaf1',
            'one.a.a2': 'leaf2',
            'one.b.b1': 'leaf3',
            'one.c.c1__literal__': '123',
        }
        self.assertEqual(
            {'one': {'a': {'a1': 'leaf1', 'a2': 'leaf2'}, 'b': {'b1': 'leaf3'}, 'c': {'c1': 123}}},
            convert(config),
        )

    def test_logging_syntax_fixes(self):
        config = {
            'root': {'handlers': 'one, two'},
            'loggers': {'zope_interface': {'level': 'DEBUG', 'handlers': 'three, four'}},
            'formatters': {'foo': {'class': 'myclass'}},
        }
        zeit.cms.logging.apply_logging_syntax_fixes(config)
        self.assertEqual(
            {
                'version': 1,
                'disable_existing_loggers': False,
                'root': {'handlers': ['one', 'two']},
                'loggers': {'zope.interface': {'level': 'DEBUG', 'handlers': ['three', 'four']}},
                'formatters': {'foo': {'()': 'myclass'}},
            },
            config,
        )
