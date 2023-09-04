from zeit.wochenmarkt.sources import ingredientsSource
import grokcore.component as grok
import logging
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.wochenmarkt.interfaces
import zope.component
import zope.component.hooks


log = logging.getLogger(__name__)


class IngredientsSearch(zeit.cms.browser.view.JSON):

    def json(self):
        term = self.request.form.get('term')
        if term:
            tags = ingredientsSource.factory.search(term)
        else:
            tags = []
        return [{'label': x.name, 'value': x.code} for x in tags]


@grok.adapter(
    zeit.wochenmarkt.interfaces.IIngredientsSource,
    zeit.cms.browser.interfaces.ICMSLayer)
@grok.implementer(zeit.cms.browser.interfaces.ISourceQueryURL)
def IngredientsSearchURL(context, request):
    base = zope.traversing.browser.absoluteURL(
        zope.component.hooks.getSite(), request)
    return (
        base + '/@@ingredients_find')
