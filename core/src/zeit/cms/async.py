import gocept.async
import martian
import sys
import zope.app.appsetup.product


def function(queue=None):
    """Decorator that marks a function for async execution.

    If no queue name is given, it is taken from product config (which is the
    sole reason this grok-based mechanism exists, so we can do the async
    wrapping at ZCML time, where we have the product config).

    """
    def decorate(func):
        frame = sys._getframe(1)
        name = '__zeit_cms_async__'
        functions = frame.f_locals.get(name, None)
        if functions is None:
            frame.f_locals[name] = functions = []
        functions.append((func, queue))
        return func
    return decorate


class GlobalAsyncFunctionsGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        functions = module_info.getAnnotation('zeit.cms.async', [])
        for func, queue in functions:
            if queue is None:
                cfg = zope.app.appsetup.product.getProductConfiguration(
                    'zeit.cms')
                queue = cfg['task-queue-async']
            setattr(module, func.__name__, gocept.async.function(queue)(func))
        return True
