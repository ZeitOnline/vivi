import grokcore.component as grok
import zope.security.adapter
import zope.security.proxy

import zeit.cms.interfaces


class TrustedAdapter(grok.Adapter):
    """zope.security.adapter.LocatingTrustedAdapterFactory for Grok."""

    grok.baseclass()

    def __new__(cls, context):
        # Trusted adapter
        instance = object.__new__(cls)
        instance.__parent__ = context
        if zope.security.proxy.removeSecurityProxy(context) is context:
            # Context is unwrapped. Basically do nothing special here.
            instance.__init__(context)
            return instance
        # Context is wrapped. Unwrap and wrap adapter
        context = zope.security.proxy.removeSecurityProxy(context)
        instance.__init__(context)
        instance = zope.security.adapter.assertLocation(instance, context)
        return zope.security.proxy.ProxyFactory(instance)


class IndirectAdapter(grok.Adapter):
    """This adapter works by adapting its context to the `interface` configured
    separately from the adapter registration itself, and declines if that is
    not possible. (All adapters are registered for the same base ICMSContent
    interface.) This way we can retrieve data stored in various DAVPropertyAdapters."""

    grok.baseclass()
    grok.context(zeit.cms.interfaces.ICMSContent)

    interface = NotImplemented
    # Subclasses usually should specify `grok.name(interface.__name__)`

    def __new__(cls, context):
        adapted = cls.interface(context, None)
        if adapted is None:
            return None
        instance = object.__new__(cls)
        instance.context = adapted
        instance.content = context
        return instance

    def __init__(self, context):
        pass  # self.context has been set by __new__() already.
