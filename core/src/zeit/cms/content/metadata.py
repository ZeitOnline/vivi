from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.tagging.tag
import zeit.wochenmarkt.categories
import zope.interface


@zope.interface.implementer(ICommonMetadata)
class CommonMetadata(zeit.cms.content.xmlsupport.XMLContentBase):

    zeit.cms.content.dav.mapProperties(ICommonMetadata, DOCUMENT_SCHEMA_NS, (
        'banner_id',
        'cap_title',
        'copyrights',
        'page',
        'ressort',
        'sub_ressort',
        'serie',
        'vg_wort_id',
        'volume',
        'year',
        'deeplink_url',

        'banner',
        'banner_content',
        'hide_adblocker_notification',
        'overscrolling',

        'advertisement_title',
        'advertisement_text',
    ))

    zeit.cms.content.dav.mapProperties(ICommonMetadata, DOCUMENT_SCHEMA_NS, (
        'access',
        'banner_outer',
        'channels',
    ), use_default=True)

    authorships = zeit.cms.content.reference.ReferenceProperty(
        '.head.author', xml_reference_name='author')
    agencies = zeit.cms.content.reference.MultiResource(
        '.head.agency', xml_reference_name='related')

    keywords = zeit.cms.tagging.tag.Tags()

    recipe_categories = zeit.wochenmarkt.categories.RecipeCategories()

    title = zeit.cms.content.property.ObjectPathProperty(
        '.body.title', ICommonMetadata['title'])
    subtitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.subtitle', ICommonMetadata['subtitle'])
    supertitle = zeit.cms.content.property.ObjectPathProperty(
        '.body.supertitle', ICommonMetadata['supertitle'])
    byline = zeit.cms.content.property.ObjectPathProperty(
        '.body.byline', ICommonMetadata['byline'])

    teaserTitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.title', ICommonMetadata['teaserTitle'])
    teaserText = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.text', ICommonMetadata['teaserText'])
    teaserSupertitle = zeit.cms.content.property.ObjectPathProperty(
        '.teaser.supertitle', ICommonMetadata['teaserSupertitle'])

    authors = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['authors'], DOCUMENT_SCHEMA_NS, 'author',
        use_default=True)

    printRessort = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['printRessort'], zeit.cms.interfaces.PRINT_NAMESPACE,
        'ressort')

    commentsPremoderate = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentsPremoderate'],
        DOCUMENT_SCHEMA_NS, 'comments_premoderate')

    commentsAllowed = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentsAllowed'], DOCUMENT_SCHEMA_NS, 'comments')

    commentSectionEnable = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentSectionEnable'],
        DOCUMENT_SCHEMA_NS, 'show_commentthread')

    product = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['product'], 'http://namespaces.zeit.de/CMS/workflow',
        'product-id')

    ir_mediasync_id = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['ir_mediasync_id'], zeit.cms.interfaces.IR_NAMESPACE,
        'mediasync_id')
    ir_article_id = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['ir_article_id'], zeit.cms.interfaces.IR_NAMESPACE,
        'article_id')

    _color_scheme = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['color_scheme'], DOCUMENT_SCHEMA_NS, 'color_scheme')

    @property
    def color_scheme(self):
        # BBB This field previously had a different meaning (for xslt/vertigo)
        # but DAVProperty/Choice type conversion is intentionally not strict.
        value = self._color_scheme
        if value not in ICommonMetadata['color_scheme'].vocabulary:
            return None
        return value

    @color_scheme.setter
    def color_scheme(self, value):
        self._color_scheme = value


@grok.subscribe(ICommonMetadata, zope.lifecycleevent.IObjectModifiedEvent)
def set_default_channel_to_ressort(context, event):
    relevant_change = False
    for description in event.descriptions:
        if not issubclass(description.interface, ICommonMetadata):
            continue
        if ('ressort' in description.attributes or
                'sub_ressort' in description.attributes):
            relevant_change = True
            break
    if not relevant_change:
        return
    if zeit.cms.content.interfaces.ISkipDefaultChannel.providedBy(context):
        return
    if not context.ressort:
        return
    if context.product and not context.product.autochannel:
        return
    channel = (context.ressort, context.sub_ressort)
    if channel in context.channels:
        return
    context.channels = context.channels + (channel,)


@grok.subscribe(ICommonMetadata, zope.lifecycleevent.IObjectModifiedEvent)
def log_access_change(context, event):
    log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
    for description in event.descriptions:
        if 'access' in description.attributes:
            access_old = zeit.cms.interfaces.ICMSContent(
                context.uniqueId).access
            if access_old == context.access:
                return
            access_old_translation = ICommonMetadata[
                'access'].source.factory.getTitle(context, access_old)
            access_new_translation = ICommonMetadata[
                'access'].source.factory.getTitle(context, context.access)
            log.log(context, _("Access changed from \"${old}\" to \"${new}\"",
                               mapping=dict(old=access_old_translation,
                                            new=access_new_translation)))
        break
    else:
        return
