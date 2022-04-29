from zope.browserpage import ViewPageTemplateFile
import grokcore.component as grok
import zeit.cms.content.sources
import zope.browser.interfaces
import zope.component
import zope.formlib.form
import zope.formlib.widget
import zope.interface


class LinkSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.cms'
    config_url = 'source-manual'
    default_filename = 'vivi-handbuch.xml'
    attribute = 'id'


LINK_SOURCE = LinkSource()


class LinkField(zope.schema.TextLine):

    def __init__(self):
        super(LinkField, self).__init__(readonly=True)


class ILink(zope.interface.Interface):

    manual_link = LinkField()


@zope.interface.implementer(ILink)
class DummyLink:

    manual_link = None


@grok.adapter(zope.interface.Interface)
@grok.implementer(ILink)
def satisfy_formlib(context):
    return DummyLink()


class LinkWidget(zope.formlib.widget.BrowserWidget):

    __call__ = ViewPageTemplateFile('manual.pt')
    # Must be set in setUpWidgets, because zope.formlib API provides no access
    # to the form from the widget, major sigh.
    key = None

    @property
    def href(self):
        terms = zope.component.getMultiAdapter(
            (LINK_SOURCE(None), self.request), zope.browser.interfaces.ITerms)
        return terms.getTerm(self.key).title


class FormMixin:

    def __init__(self, context, request):
        super(FormMixin, self).__init__(context, request)
        self.form_fields += zope.formlib.form.FormFields(ILink)

    def setUpWidgets(self, *args, **kwargs):
        super(FormMixin, self).setUpWidgets(*args, **kwargs)
        # Skip the zope.metaconfigure baseclass synthesized by <browser:page>
        cls = self.__class__.__bases__[0]
        self.widgets['manual_link'].key = '.'.join([
            cls.__module__, cls.__name__])
