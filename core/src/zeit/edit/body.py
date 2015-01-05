import grokcore.component as grok
import z3c.traverser.interfaces
import zope.interface
import zope.location.interfaces
import zope.publisher.interfaces
import zope.traversing.adapters
import zope.traversing.interfaces


class Traverser(grok.Adapter):

    grok.baseclass()
    grok.implements(zope.traversing.interfaces.ITraversable)

    body_name = NotImplemented
    body_interface = NotImplemented

    def traverse(self, name, furtherPath):
        if name == self.body_name:
            body = self.body_interface(self.context, None)
            if body is not None:
                return body
        else:
            # XXX zope.component does not offer an API to get the next adapter
            # that is less specific than the current one. So we hard-code the
            # default.
            return zope.traversing.adapters.DefaultTraversable(
                self.context).traverse(name, furtherPath)


class PublishTraverser(object):
    """
    Register like this::

      <adapter
        factory="z3c.traverser.traverser.PluggableTraverser"
        for="CONTENT_TYPE_INTERFACE
             zeit.cms.browser.interfaces.ICMSLayer"
        />
      <subscriber
        factory="zeit.edit.body.PublishTraverser"
        for="BODY_INTERFACE
             zeit.cms.browser.interfaces.ICMSLayer"
        provides="z3c.traverser.interfaces.ITraverserPlugin"
        />
    """

    zope.interface.implements(z3c.traverser.interfaces.IPluggableTraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        try:
            return zope.traversing.interfaces.ITraversable(
                self.context).traverse(name, None)
        except zope.location.interfaces.LocationError:
            raise zope.publisher.interfaces.NotFound(
                self.context, name, request)
