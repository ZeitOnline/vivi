# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import xml.sax.saxutils
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.source
import zope.component.hooks
import zope.formlib.interfaces
import zope.i18n


class AutocompleteSourceQuery(grok.MultiAdapter,
                              zeit.cms.browser.view.Base):

    # XXX copy&paste&tweak from zeit.find.browser.autocomplete, can this be
    # refactored?

    grok.adapts(
        zeit.cms.tagging.interfaces.IWhitelistSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zope.formlib.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def __call__(self):
        return (
            u'<input type="text" class="autocomplete" '
            u'placeholder={placeholder} '
            u'cms:autocomplete-source="{url}" />').format(
            # XXX make use of ISourceQueryURL mechanism
            url=self.url(
                zope.component.hooks.getSite(), '@@zeit.cms.tagging.search'),
            placeholder=xml.sax.saxutils.quoteattr(
                zope.i18n.translate(_('Type to find entries ...'),
                                    context=self.request)))


class WhitelistSearch(zeit.cms.browser.view.JSON):

    @property
    def whitelist(self):
        return zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)

    def json(self):

        term = self.request.form.get('term')
        if term:
            results = self.whitelist.search(term)
        else:
            results = []
        return [dict(label=result.label, value=result.uniqueId)
                for result in results]


class LocationSearch(zeit.cms.browser.view.JSON):

    def json(self):
        term = self.request.form.get('term')
        if term:
            results = zeit.cms.tagging.source.locationSource.factory.search(
                term)
        else:
            results = []
        return [dict(label=x, value=x) for x in results]


@grok.adapter(
    zeit.cms.tagging.source.ILocationSource,
    zeit.cms.browser.interfaces.ICMSLayer)
@grok.implementer(zeit.cms.browser.interfaces.ISourceQueryURL)
def LocationSearchURL(context, request):
    base = zope.traversing.browser.absoluteURL(
        zope.component.hooks.getSite(), request)
    return (
        base + '/@@zeit.cms.tagging.location.search')
