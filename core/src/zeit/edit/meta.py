import gocept.lxml.interfaces
import grokcore.component
import martian
import six
import zeit.edit.block
import zeit.edit.interfaces
import zope.component.zcml
import zope.interface


class NoneGuard:
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
            result = '__NONE__'
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
                name=six.text_type(func.__name__))
        return True


class SimpleElementGrokker(martian.ClassGrokker):

    martian.component(zeit.edit.block.SimpleElement)

    def execute(self, context, config, **kw):
        for_ = (context.area, gocept.lxml.interfaces.IObjectified)
        provides = list(zope.interface.implementedBy(context))[0]

        config.action(
            discriminator=('adapter', for_, provides, context.type),
            callable=zope.component.provideAdapter,
            args=(context, for_, provides, context.type),
        )
        return True


class ElementFactoryGrokker(martian.ClassGrokker):

    martian.component(zeit.edit.block.ElementFactory)
    martian.directive(grokcore.component.context)

    def execute(self, factory, config, context, **kw):
        name = factory.element_type = factory.produces.type
        provides = list(zope.interface.implementedBy(factory))[0]
        config.action(
            discriminator=('adapter', context, provides, name),
            callable=zope.component.provideAdapter,
            args=(factory, (context,), provides, name),
        )
        return True
