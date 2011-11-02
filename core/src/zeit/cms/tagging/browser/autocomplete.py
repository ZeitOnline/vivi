# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import xml.sax.saxutils
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.content.interfaces
import zeit.find.browser.find
import zope.formlib.interfaces
import zope.i18n


class AutocompleteSourceQuery(grokcore.component.MultiAdapter,
                              zeit.cms.browser.view.Base):

    # XXX copy&paste&tweak from zeit.find.browser.autocomplete, can this be
    # refactored?

    grokcore.component.adapts(
        zeit.cms.tagging.interfaces.IWhitelistTagSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(zope.formlib.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def __call__(self):
        return (
            '<input type="text" class="autocomplete" '
            'placeholder={placeholder} '
            'cms:autocomplete-source="{url}" />').format(
                url=self.url(self.source.whitelist, '@@search'),
                placeholder=xml.sax.saxutils.quoteattr(
                    zope.i18n.translate(_('Type to find entries ...'),
                                        context=self.request)))


class Search(zeit.cms.browser.view.JSON):

    def json(self):
        term = self.request.form.get('term')
        if term:
            results = self.context.search(term)
        else:
            results = []
        return [dict(label=result.label, value=result.uniqueId)
                for result in results]
