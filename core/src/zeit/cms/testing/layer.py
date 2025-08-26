import inspect
import logging

import plone.testing


class Layer(plone.testing.Layer):
    def __init__(self, bases=None, name=None):
        if bases is not None and not isinstance(bases, tuple):
            bases = (bases,)
        if name is None:
            name = self.__class__.__name__
        for item in inspect.stack():
            if item.function == '<module>':
                module = item.frame.f_globals['__name__']
                break
        super().__init__(bases, name, module)


class LoggingLayer(Layer):
    def setUp(self):
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('zeit').setLevel(logging.DEBUG)
        logging.getLogger('zeit.cms.repository').setLevel(logging.INFO)
        logging.getLogger('selenium').setLevel(logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.INFO)
        logging.getLogger('waitress').setLevel(logging.ERROR)


LOGGING_LAYER = LoggingLayer()
