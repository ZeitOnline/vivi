import grokcore.component as grok
import zope.security.adapter
import zope.security.proxy


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
