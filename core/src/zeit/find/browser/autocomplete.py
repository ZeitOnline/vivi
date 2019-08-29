import grokcore.component as grok
import urllib
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.find.interfaces
import zeit.find.search
import zope.component
import zope.component.hooks
import zope.traversing.browser


class SimpleFind(zeit.cms.browser.view.JSON):

    def json(self):
        term = self.request.form.pop('term', None)
        if term:
            elastic = zope.component.getUtility(
                zeit.find.interfaces.ICMSSearch)
            results = elastic.search(
                zeit.find.search.query(autocomplete=term, **self.request.form))
        else:
            results = []
        return [
            dict(label=(result.get('title') or
                        result.get('teaser') or
                        result['url']),
                 value=zeit.cms.interfaces.ID_NAMESPACE[:-1] + result['url'])
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
    # Since IAutocompleteSource is only a marker and we don't have a baseclass,
    # hasattr is the overall easiest spelling, even though it's a bit kludgy.
    if hasattr(context, 'additional_query_conditions'):
        query += '&' + urllib.urlencode(context.additional_query_conditions)
    return ('%s/@@simple_find?%s' % (base, query))
