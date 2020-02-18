from __future__ import absolute_import
import ast
import six

try:
    import fluent.handler
except ImportError:
    pass  # soft dependency
else:
    class FluentRecordFormatter(fluent.handler.FluentRecordFormatter):
        """Work around the fact that `logging.fileConfig` (which most clients
        use) is not based on `logging.dictConfig` and thus is less expressive,
        especially concerning Formatter instantiation: it only supports a
        (string) `format=` parameter, and nothing else. Since
        FluentRecordFormatter needs a dict, we call literal_eval so it works.
        """

        def __init__(self, fmt=None, datefmt=None, **kw):
            if (isinstance(fmt, six.string_types) and
                    fmt.strip().startswith('{')):
                fmt = ast.literal_eval(fmt)
            super(FluentRecordFormatter, self).__init__(fmt, **kw)
