import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.cms.tagging.interfaces
import zope.component
import zope.component.hooks
import zope.location.interfaces
import zope.publisher.interfaces
import zope.site.interfaces
import zope.traversing.browser
import zope.traversing.browser.absoluteurl
import zope.traversing.interfaces


class TagTraverser(grok.MultiAdapter):

    zope.interface.implements(zope.traversing.interfaces.ITraversable)
    grok.adapts(
        zope.site.interfaces.IRootFolder,
        zope.publisher.interfaces.IRequest)
    grok.name('tag')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        # As we encoded the code in `AbsoluteURL` we have to undo the escaping.
        name = name.decode('unicode_escape')
        tag = whitelist.get(name)
        if tag is None:
            raise zope.location.interfaces.LocationError(self.context, name)
        return tag


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    zope.component.adapts(zeit.cms.tagging.interfaces.ITag,
                          zeit.cms.browser.interfaces.ICMSLayer)

    def __str__(self):
        base = zope.traversing.browser.absoluteURL(
            zope.component.hooks.getSite(), self.request)
        # `zeit.retresco` possibly generates `.code` with unicode characters so
        # we have to escape them to get a valid url.
        return base + '/++tag++' + self.context.code.encode('unicode_escape')
