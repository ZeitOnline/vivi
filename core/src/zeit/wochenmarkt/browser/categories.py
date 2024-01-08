import logging

import grokcore.component as grok
import zope.component
import zope.component.hooks

from zeit.wochenmarkt.sources import recipeCategoriesSource
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.wochenmarkt.interfaces


log = logging.getLogger(__name__)


class RecipeCategoriesSearch(zeit.cms.browser.view.JSON):
    def json(self):
        term = self.request.form.get('term')
        if term:
            categories = recipeCategoriesSource.factory.search(term)
        else:
            categories = []
        return [{'label': x.name, 'value': x.code} for x in categories]


@grok.adapter(
    zeit.wochenmarkt.interfaces.IRecipeCategoriesSource, zeit.cms.browser.interfaces.ICMSLayer
)
@grok.implementer(zeit.cms.browser.interfaces.ISourceQueryURL)
def CategoriesSearchURL(context, request):
    base = zope.traversing.browser.absoluteURL(zope.component.hooks.getSite(), request)
    return base + '/@@recipe_categories_find'
