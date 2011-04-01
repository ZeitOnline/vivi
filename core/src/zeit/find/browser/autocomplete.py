# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import urllib
import xml.sax.saxutils
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.find.browser.find
import zope.formlib.interfaces
import zope.i18n


class AutocompleteSourceQuery(grokcore.component.MultiAdapter,
                              zeit.cms.browser.view.Base):

    grokcore.component.adapts(
        zeit.cms.content.interfaces.IAutocompleteSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(zope.formlib.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def __call__(self):
        return (
            '<input type="text" class="autocomplete" '
            'placeholder={placeholder} '
            'cms:autocomplete-source="{url}?{query}" />').format(
                url=self.url(zope.site.hooks.getSite(), '@@simple_find'),
                query=urllib.urlencode(
                    [('types:list', self.source.get_check_types())],
                    doseq=True),
                placeholder=xml.sax.saxutils.quoteattr(
                    zope.i18n.translate(_('Type to find entries ...'),
                                        context=self.request)))


class SimpleFind(zeit.cms.browser.view.JSON):

    def json(self):
        term = self.request.form.get('term')
        types = self.request.form.get('types', ())
        if term:
            results = zeit.find.search.search(
                zeit.find.search.query(fulltext=term,
                                       types=types))
        else:
            results = []
        return [
            dict(label=(result.get('teaser_title') or
                        result.get('title') or
                        result['uniqueId']),
                 value=result['uniqueId'])
            for result in results]
