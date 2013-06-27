# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import grokcore.component
import xml.sax.saxutils
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.tagging.interfaces
import zope.formlib.interfaces
import zope.i18n


class AutocompleteSourceQuery(grokcore.component.MultiAdapter,
                              zeit.cms.browser.view.Base):

    # XXX copy&paste&tweak from zeit.find.browser.autocomplete, can this be
    # refactored?

    grokcore.component.adapts(
        zeit.cms.tagging.interfaces.IWhitelistSource,
        zeit.cms.browser.interfaces.ICMSLayer)
    grokcore.component.provides(zope.formlib.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.source = source
        self.request = request

    def __call__(self):
        return (
            u'<input type="text" class="autocomplete" '
            u'placeholder={placeholder} '
            u'cms:autocomplete-source="{url}" />').format(
                url=self.url(zope.site.hooks.getSite(),
                             '@@zeit.cms.tagging.search'),
                placeholder=xml.sax.saxutils.quoteattr(
                    zope.i18n.translate(_('Type to find entries ...'),
                                        context=self.request)))


class Search(zeit.cms.browser.view.JSON):

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
