# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.edit.interfaces
import martian
import zope.component.zcml


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


class GlobalRuleGlobsGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        globs = module_info.getAnnotation('zeit.edit.globs', [])
        for func, adapts in globs:
            zope.component.zcml.adapter(
                config,
                for_=(adapts,),
                factory=(NoneGuard(func),),
                provides=zeit.edit.interfaces.IRuleGlob,
                name=unicode(func.func_name))
        return True
