from collections import namedtuple
from zeit.content.modules.recipelist import Ingredient
from zeit.wochenmarkt.categories import RecipeCategory
import json
import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.interfaces
import zeit.wochenmarkt.interfaces
import zope.app.appsetup.appsetup
import zope.app.pagetemplate
import zope.component.hooks
import zope.formlib.itemswidgets
import zope.formlib.source
import zope.formlib.widget
import zope.lifecycleevent
import zope.schema.interfaces


class IngredientsWidget(
        grok.MultiAdapter,
        zope.formlib.widget.SimpleInputWidget,
        zeit.cms.browser.view.Base):
    """Widget to edit ingredients on context.

    """

    grok.adapts(
        zope.schema.interfaces.ITuple,
        zeit.wochenmarkt.interfaces.IIngredientsSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zope.formlib.interfaces.IInputWidget)

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'ingredients_widget.pt')

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    @property
    def autocomplete_source_url(self):
        return self.url(
            zope.component.hooks.getSite(), '@@ingredients_find')

    @property
    def uuid(self):
        return zeit.cms.content.interfaces.IUUID(self.context.context).id

    def _toFormValue(self, value):
        return json.dumps([{
            'code': x.code, 'label': x.label,
            'amount': x.amount, 'unit': x.unit,
            'details': x.details
        } for x in value or ()])

    def _toFieldValue(self, value):
        data = json.loads(value)
        return tuple([
            Ingredient(
                x['code'], x['label'],
                amount=x['amount'],
                unit=x['unit'],
                details=x['details']
            ) for x in data])


class RecipeCategoriesWidget(
        grok.MultiAdapter,
        zope.formlib.widget.SimpleInputWidget,
        zeit.cms.browser.view.Base):
    """Widget to edit recipe categories on context.

    """

    grok.adapts(
        zope.schema.interfaces.ITuple,
        zeit.wochenmarkt.interfaces.IRecipeCategoriesSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zope.formlib.interfaces.IInputWidget)

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'categories_widget.pt')

    def __init__(self, context, source, request):
        super().__init__(context, request)
        self.source = source

    def __call__(self):
        return self.template()

    @property
    def autocomplete_source_url(self):
        return self.url(
            zope.component.hooks.getSite(), '@@recipe_categories_find')

    @property
    def uuid(self):
        return zeit.cms.content.interfaces.IUUID(self.context.context).id

    def _toFormValue(self, value):
        return json.dumps([{
            'code': x.code, 'label': x.name
        } for x in value or ()])

    def _toFieldValue(self, value):
        data = json.loads(value)
        return tuple([
            RecipeCategory(x['code'], x['label']) for x in data])


class DisplayWidget(grok.MultiAdapter,
                    zope.formlib.itemswidgets.ItemsWidgetBase):

    grok.adapts(
        zope.schema.interfaces.ITuple,
        zeit.wochenmarkt.interfaces.IRecipeCategoriesSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zope.formlib.interfaces.IDisplayWidget)

    template = zope.app.pagetemplate.ViewPageTemplateFile(
        'display-recipe-categories.pt')

    def __init__(self, field, source, request):
        super().__init__(
            field,
            zope.formlib.source.IterableSourceVocabulary(source, request),
            request)

    def __call__(self):
        return self.template()

    def items(self):
        items = []
        RecipeCategory = namedtuple('RecipeCategory', ['text'])
        for item in self._getFormValue():
            text = self.textForValue(self.vocabulary.getTerm(item))
            items.append(RecipeCategory(text))
        return items
