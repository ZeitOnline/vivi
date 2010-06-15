# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.interfaces
import zope.component.zcml
import zope.configuration.fields
import zope.interface
import zope.security.metaconfigure


class IGlobsDirective(zope.interface.Interface):

    module = zope.configuration.fields.GlobalObject(
        title=u"Module containing globs")


class NoneGuard(object):
    """An IRuleGlob must never return None, because then it would not show up
    in the getAdapters() result, so its name would be undefined leading to
    eval-errors.

    XXX: using an inline function or lambda to do the wrapping didn't work, so
    we use instances of this class instead.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kw):
        result = self.func(*args, **kw)
        if result is None:
            result= '__NONE__'
        return result


def globs_directive(_context, module):
    for func, adapts in module._globs:
        zope.component.zcml.adapter(
            _context,
            for_=(adapts,),
            factory=(NoneGuard(func),),
            provides=zeit.content.cp.interfaces.IRuleGlob,
            name=unicode(func.func_name))
