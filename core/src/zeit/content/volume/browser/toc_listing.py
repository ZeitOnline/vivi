import zeit.cms.browser.listing
from zeit.cms.i18n import MessageFactory as _


class CheckColumn(zeit.cms.browser.listing.GetterColumn):

    def cell_formatter(self, value, item, formatter):
        if value:
            return '&#10004;'
        else:
            return ''


class TocListing(zeit.cms.browser.listing.Listing):

    teaser_image_available = _('Teaser image available')
    supertitle_available = _('Supertitle available')
    contenttype = _('Content-Typ')
    availability = _('Availability')
    is_urgent = _('is urgent')
    is_seo_optimized = _('is SEO optimized')
    ressort = _('Ressort')
    rows = _('rows')

    css_class = 'contentListing hasMetadata tocListing'

    columns = (
        zeit.cms.browser.listing.Listing.columns[0:5] +
        (zeit.cms.browser.listing.GetterColumn(
            _('Supertitle'),
            name='supertitle',
            getter=lambda t, c: t.supertitle),) +
        zeit.cms.browser.listing.Listing.columns[5:6] +
        (zeit.cms.browser.listing.GetterColumn(
            _('Ressort'),
            name='ressort',
            getter=lambda t, c: t.printRessort),) +
        zeit.cms.browser.listing.Listing.columns[8:9] +
        (CheckColumn(
            _('Urgent'),
            name='urgent',
            getter=lambda t, c: t.workflow.urgent),
            CheckColumn(
                _('status-seo-optimized'),
                name='seo-optimized',
                getter=lambda t, c: t.workflow.seo_optimized),) +
        zeit.cms.browser.listing.Listing.columns[8:10] +
        (CheckColumn(
            _('Teaserimage'),
            name='teaserimage',
            getter=lambda t, c: t.teaserimage is not None),) +
        zeit.cms.browser.listing.Listing.columns[10:]
    )
