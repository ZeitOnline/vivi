import z3c.traverser.traverser
import zope.interface
import zope.publisher.skinnable

import zeit.cms.browser.interfaces


class LayerAddTraverser(z3c.traverser.traverser.ContainerTraverserPlugin):
    """Add an additional layer to the request, if there is one specified.

    Used to set specific layers for repository content and workingcopy content,
    so the behaviour can be easily customized based on content displayed in the
    repository or in the workingcopy.

    """

    def publishTraverse(self, request, name):
        """Resolve the container and add an additional layer if possible."""
        result = super().publishTraverse(request, name)
        layer = zeit.cms.browser.interfaces.IAdditionalLayer(result, None)
        if layer is not None:
            # The skinlayer and the additional layer both inherit from
            # ICMSLayer, this leads to a diamond shaped problem when resolving
            # the MRO. Using alsoProvides, the new layer would be added to the
            # end, which leads to the wrong thing (ICMSLayer comes after
            # IDefaultBrowserLayer). Therefore we insert the new layer manually
            # in front of the skin, which leads to the order we want / need.
            # We know what we are doing, trust us. Please. ;)
            ifaces = list(zope.interface.directlyProvidedBy(request))
            ifaces.insert(0, layer)
            zope.interface.directlyProvides(request, *ifaces)
        return result
