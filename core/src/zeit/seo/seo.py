import grokcore.component as grok

from zeit.retresco.interfaces import ISkipEnrich
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.seo.interfaces


@grok.implementer(zeit.seo.interfaces.ISEO)
class SEO(zeit.cms.content.dav.DAVPropertiesAdapter):
    grok.adapts(zeit.cms.interfaces.ICMSContent)

    html_title = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['html_title'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'html-meta-title',
    )

    html_description = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['html_description'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'html-meta-description',
    )

    meta_robots = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['meta_robots'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'html-meta-robots',
    )

    hide_timestamp = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['hide_timestamp'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'html-meta-hide-timestamp',
    )

    disable_intext_links = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['disable_intext_links'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'seo-disable-intext-links',
    )

    keyword_entity_type = zeit.cms.content.dav.DAVProperty(
        zeit.seo.interfaces.ISEO['keyword_entity_type'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'seo-keyword-entity-type',
    )

    def __init__(self, context):
        self.context = context

    @property  # Write is handled by .browser.form.SEOEdit
    def disable_enrich(self):
        return ISkipEnrich.providedBy(self.context)
