import doctest
import re

import zope.testing.renormalizing


checker = zope.testing.renormalizing.RENormalizing(
    [
        (re.compile(r'\d{4} \d{1,2} \d{1,2}  \d\d:\d\d:\d\d'), '<FORMATTED DATE>'),
        (re.compile('0x[0-9a-f]+'), '0x...'),
        (re.compile(r'/\+\+noop\+\+[0-9a-f]+'), ''),
        (re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '<GUID>'),
    ]
)


def remove_exception_module(msg):
    """Copy&paste so we keep the exception message and support multi-line."""
    start, end = 0, len(msg)
    name_end = msg.find(':', 0, end)
    i = msg.rfind('.', 0, name_end)
    if i >= 0:
        start = i + 1
    return msg[start:end]


doctest._strip_exception_details = remove_exception_module


optionflags = (
    doctest.REPORT_NDIFF
    + doctest.NORMALIZE_WHITESPACE
    + doctest.ELLIPSIS
    + doctest.IGNORE_EXCEPTION_DETAIL
)


def FunctionalDocFileSuite(*paths, **kw):
    import zeit.cms.testing  # break circular import

    layer = kw.pop('layer', zeit.cms.testing.WSGI_LAYER)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    globs = kw.setdefault('globs', {})
    globs['getRootFolder'] = lambda: layer['zodbApp']
    globs['layer'] = layer
    kw.setdefault('checker', checker)
    kw.setdefault('optionflags', optionflags)
    kw['encoding'] = 'utf-8'

    test = doctest.DocFileSuite(*paths, **kw)
    test.layer = layer

    return test
