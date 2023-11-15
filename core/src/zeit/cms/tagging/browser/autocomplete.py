import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.source
import zope.component.hooks


class WhitelistSearch(zeit.cms.browser.view.JSON):
    @property
    def whitelist(self):
        return zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)

    def json(self):
        term = self.request.form.get('term')
        if term:
            results = self.whitelist.search(term)
        else:
            results = []
        return [{'label': x.title, 'value': x.uniqueId} for x in results]


@grok.adapter(zeit.cms.tagging.source.IWhitelistSource, zeit.cms.browser.interfaces.ICMSLayer)
@grok.implementer(zeit.cms.browser.interfaces.ISourceQueryURL)
def WhitelistSearchURL(context, request):
    base = zope.traversing.browser.absoluteURL(zope.component.hooks.getSite(), request)
    return base + '/@@zeit.cms.tagging.search'


class LocationSearch(zeit.cms.browser.view.JSON):
    def json(self):
        term = self.request.form.get('term')
        if term:
            tags = zeit.cms.tagging.source.locationSource.factory.search(term)
        else:
            tags = []
        return [{'label': x.label, 'value': x.uniqueId} for x in tags]


@grok.adapter(zeit.cms.tagging.source.ILocationSource, zeit.cms.browser.interfaces.ICMSLayer)
@grok.implementer(zeit.cms.browser.interfaces.ISourceQueryURL)
def LocationSearchURL(context, request):
    base = zope.traversing.browser.absoluteURL(zope.component.hooks.getSite(), request)
    return base + '/@@zeit.cms.tagging.location.search'
