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
from zeit.content.modules.recipelist import Ingredient


class Widget(grok.MultiAdapter,
             zope.formlib.widget.SimpleInputWidget,
             zeit.cms.browser.view.Base):
    """Widget to edit recipes on context.

    """

    grok.adapts(
        zope.schema.interfaces.ITuple,
        zeit.wochenmarkt.interfaces.IIngredientsSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zope.formlib.interfaces.IInputWidget)

    template = zope.app.pagetemplate.ViewPageTemplateFile('widget.pt')

    def __init__(self, context, source, request):
        super(Widget, self).__init__(context, request)
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
            'amount': x.amount, 'unit': x.unit
        } for x in value or ()])

    def _toFieldValue(self, value):
        data = json.loads(value)
        return tuple([
            Ingredient(
                x['code'], x['label'], x['amount'], x['unit']
            ) for x in data])
