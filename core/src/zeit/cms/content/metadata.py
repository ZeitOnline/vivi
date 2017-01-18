import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.tagging.tag
import zope.interface


class CommonMetadata(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(
        zeit.cms.content.interfaces.ICommonMetadata)

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        (
            'banner_id',
            'cap_title',
            'color_scheme',
            'copyrights',
            'page',
            'ressort',
            'sub_ressort',
            'vg_wort_id',
            'volume',
            'year',
            'mobile_alternative',
            'deeplink_url',
            'breadcrumb_title',

            'banner',
            'banner_content',
            'breaking_news',
            'countings',
            'foldable',
            'in_rankings',
            'is_content',
            'minimal_header',
            'lead_candidate',
            'push_news',
            'rebrush_website_content',

            'tldr_title',
            'tldr_text',
            'tldr_milestone',
            'tldr_date',

            'advertisement_title',
            'advertisement_text',
            'bigshare_buttons',
        ))

    zeit.cms.content.dav.mapProperties(
        zeit.cms.content.interfaces.ICommonMetadata,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('access',), use_default=True)

    authors = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['authors'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'author',
        use_default=True)

    authorships = zeit.cms.content.reference.ReferenceProperty(
        '.head.author', xml_reference_name='author')

    keywords = zeit.cms.tagging.tag.Tags()

    title = zeit.cms.content.property.ObjectPathProperty(
        '.body.title',
        zeit.cms.content.interfaces.ICommonMetadata['title'])
    subtitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.subtitle',
        zeit.cms.content.interfaces.ICommonMetadata['subtitle'])
    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.supertitle',
        zeit.cms.content.interfaces.ICommonMetadata['supertitle'])
    byline = zeit.cms.content.property.ObjectPathProperty(
        '.body.byline',
        zeit.cms.content.interfaces.ICommonMetadata['byline'])

    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.title',
        zeit.cms.content.interfaces.ICommonMetadata['teaserTitle'])
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.text',
        zeit.cms.content.interfaces.ICommonMetadata['teaserText'])
    teaserSupertitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.supertitle',
        zeit.cms.content.interfaces.ICommonMetadata['teaserSupertitle'])

    printRessort = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['printRessort'],
        zeit.cms.interfaces.PRINT_NAMESPACE, 'ressort')

    commentsAllowed = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['commentsAllowed'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'comments')

    commentSectionEnable = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['commentSectionEnable'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'show_commentthread')

    dailyNewsletter = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['dailyNewsletter'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'DailyNL')

    _product_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        'http://namespaces.zeit.de/CMS/workflow', 'product-id')
    _product_text = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        'http://namespaces.zeit.de/CMS/workflow', 'product-name')

    _serie = zeit.cms.content.dav.DAVProperty(
        zope.schema.TextLine(),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'serie')

    @property
    def product(self):
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'product'].source(self)
        for value in source:
            if value.id == self._product_id:
                return value

    @product.setter
    def product(self, value):
        if value is not None:
            if self._product_id == value.id:
                return
            self._product_id = value.id
            self._product_text = value.title
        else:
            self._product_id = None
            self._product_text = None

    @property
    def product_text(self):
        return self._product_text

    _channels = zeit.cms.content.dav.DAVProperty(
        zope.schema.Tuple(value_type=zope.schema.TextLine()),
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'channels')

    @property
    def serie(self):
        source = zeit.cms.content.interfaces.ICommonMetadata[
            'serie'].source(self)
        return source.factory.values.get(self._serie)

    @serie.setter
    def serie(self, value):
        if value is not None:
            if self._serie != value.serienname:
                self._serie = value.serienname
        else:
            self._serie = None

    @property
    def channels(self):
        if self._channels:
            return tuple(tuple(x.split(' ') if ' ' in x else (x, None))
                         for x in self._channels)
        else:
            return ()

    @channels.setter
    def channels(self, value):
        self._channels = tuple(' '.join([x for x in channel if x])
                               for channel in value)

    storystreams = zeit.cms.content.dav.DAVProperty(
        zeit.cms.content.interfaces.ICommonMetadata['storystreams'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS, 'storystreams',
        use_default=True)


@grok.subscribe(
    zeit.cms.content.interfaces.ICommonMetadata,
    zope.lifecycleevent.IObjectModifiedEvent)
def set_default_channel_to_ressort(context, event):
    relevant_change = False
    for description in event.descriptions:
        if (not issubclass(
                description.interface,
                zeit.cms.content.interfaces.ICommonMetadata)):
            continue
        if ('ressort' in description.attributes or
                'sub_ressort' in description.attributes):
            relevant_change = True
            break
    if not relevant_change:
        return
    if not context.ressort:
        return
    if context.product and not context.product.autochannel:
        return
    channel = (context.ressort, context.sub_ressort)
    if channel in context.channels:
        return
    context.channels = context.channels + (channel,)
