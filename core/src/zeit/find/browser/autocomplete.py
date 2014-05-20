# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import urllib
import xml.sax.saxutils
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zope.formlib.interfaces
import zope.i18n


class AutocompleteSourceQuery(grok.MultiAdapter,
                              zeit.cms.browser.view.Base):

    grok.adapts(
        zeit.cms.content.interfaces.IAutocompleteSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grok.provides(zope.formlib.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def __call__(self):
        return (
            u'<input type="text" class="autocomplete" '
            u'placeholder={placeholder} '
            u'cms:autocomplete-source="{url}?{query}" />').format(
            # XXX make use of ISourceQueryURL mechanism
            url=self.url(zope.site.hooks.getSite(), '@@simple_find'),
            query=urllib.urlencode(
                [('types:list', self.source.get_check_types())],
                doseq=True),
            placeholder=xml.sax.saxutils.quoteattr(
                zope.i18n.translate(
                    _('Type to find entries ...'), context=self.request)))


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
