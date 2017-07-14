import gocept.async
import logging
import martian
import sys
import zope.app.appsetup.product


log = logging.getLogger(__name__)


def function(queue=None, principal=None):
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
        functions.append((func, queue, principal))
        return func
    return decorate


class GlobalAsyncFunctionsGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        functions = module_info.getAnnotation('zeit.cms.async', [])
        for func, queue, principal in functions:
            if queue is None:
                queue = 'async'
            if principal is not None:
                package, key = principal
                principal = zope.app.appsetup.product.getProductConfiguration(
                    package)[key]
            cfg = zope.app.appsetup.product.getProductConfiguration(
                'zeit.cms') or {}
            queuename = cfg.get('task-queue-%s' % queue, '')
            if not queuename:
                # Should only happen for i18nextract.
                log.warning(
                    'Missing product config zeit.cms:task-queue-%s', queue)
            setattr(module, func.__name__, gocept.async.function(
                queuename, principal)(func))
        return True
