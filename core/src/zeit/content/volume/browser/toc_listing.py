import json

from zope.cachedescriptors.property import Lazy as cachedproperty
import zope.browser.interfaces
import zope.component
import zope.i18n

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.browser.listing
import zeit.cms.content.interfaces
import zeit.cms.content.sources


class CheckColumn(zeit.cms.browser.listing.GetterColumn):
    def cell_formatter(self, value, item, formatter):
        if value:
            return '&#10004;'
        else:
            return ''

    def getSortKey(self, item, formatter):
        value = super().getSortKey(item, formatter)
        return bool(value)


class TocListing(zeit.cms.browser.listing.Listing):
    css_class = 'contentListing hasMetadata tocListing'

    columns = (
        zeit.cms.browser.listing.Listing.columns[0:4]
        + (
            zeit.cms.browser.listing.GetterColumn(
                _('Supertitle'), name='supertitle', getter=lambda t, c: t.supertitle
            ),
        )
        + zeit.cms.browser.listing.Listing.columns[4:6]
        + (
            zeit.cms.browser.listing.GetterColumn(
                _('Ressort'), name='ressort', getter=lambda t, c: t.printRessort
            ),
        )
        + (
            CheckColumn(_('Urgent'), name='urgent', getter=lambda t, c: t.workflow.urgent),
            CheckColumn(
                _('status-seo-optimized'),
                name='seo-optimized',
                getter=lambda t, c: t.workflow.seo_optimized,
            ),
        )
        + zeit.cms.browser.listing.Listing.columns[9:10]
        + (
            CheckColumn(
                _('Teaserimage'), name='teaserimage', getter=lambda t, c: t.teaserimage is not None
            ),
        )
        + (
            zeit.cms.browser.listing.GetterColumn(
                _('Access'), name='access', getter=lambda t, c: t.access
            ),
            zeit.cms.browser.listing.GetterColumn(
                _('Type'), name='content_type', getter=lambda t, c: t.type
            ),
        )
        + zeit.cms.browser.listing.Listing.columns[10:]
    )

    def _source_values(self, source, use_token):
        terms = zope.component.getMultiAdapter(
            (source, self.request), zope.browser.interfaces.ITerms
        )
        result = {}
        for value in source:
            term = terms.getTerm(value)
            key = term.token if use_token else value
            result[key] = zope.i18n.translate(term.title, context=self.request)
        return json.dumps(result)

    @cachedproperty
    def access_values(self):
        return self._source_values(
            zeit.cms.content.interfaces.ICommonMetadata['access'].source(self.context),
            use_token=False,
        )

    @cachedproperty
    def type_values(self):
        return self._source_values(
            zeit.cms.content.sources.CMSContentTypeSource()(None), use_token=True
        )
