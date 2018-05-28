import grokcore.component as grok
import urllib
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zope.component.hooks
import zope.traversing.browser


class SimpleFind(zeit.cms.browser.view.JSON):

    def json(self):
        term = self.request.form.get('term')
        types = self.request.form.get('types', ())
        if term:
            term = term.lower().strip()
            results = zeit.find.search.search(
                zeit.find.search.suggest_query(term, 'title', types))
        else:
            results = []
        return [
            dict(label=(result.get('teaser_title') or
                        result.get('title') or
                        result['uniqueId']),
                 value=result['uniqueId'])
            for result in results]


@grok.adapter(
    zeit.cms.content.interfaces.IAutocompleteSource,
    zeit.cms.browser.interfaces.ICMSLayer)
@grok.implementer(zeit.cms.browser.interfaces.ISourceQueryURL)
def SimpleFindURL(context, request):
    base = zope.traversing.browser.absoluteURL(
        zope.component.hooks.getSite(), request)
    query = urllib.urlencode(
        [('types:list', context.get_check_types())], doseq=True)
    return ('%s/@@simple_find?%s' % (base, query))
