from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.interfaces import DOCUMENT_SCHEMA_NS
import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.content.property
import zeit.cms.content.reference
import zeit.cms.content.xmlsupport
import zeit.cms.tagging.tag
import zope.interface


class CommonMetadata(zeit.cms.content.xmlsupport.XMLContentBase):

    zope.interface.implements(ICommonMetadata)

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
        'banner_outer',
        'hide_adblocker_notification',
        'lead_candidate',
        'overscrolling',

        'tldr_title',
        'tldr_text',
        'tldr_milestone',
        'tldr_date',

        'advertisement_title',
        'advertisement_text',
    ))

    zeit.cms.content.dav.mapProperties(
        ICommonMetadata, DOCUMENT_SCHEMA_NS, ('access',), use_default=True)

    authors = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['authors'], DOCUMENT_SCHEMA_NS, 'author',
        use_default=True)

    authorships = zeit.cms.content.reference.ReferenceProperty(
        '.head.author', xml_reference_name='author')

    keywords = zeit.cms.tagging.tag.Tags()

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

    printRessort = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['printRessort'], zeit.cms.interfaces.PRINT_NAMESPACE,
        'ressort')

    commentsPremoderate = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentsPremoderate'],
        DOCUMENT_SCHEMA_NS, 'comments_premoderate')

    commentsAllowed = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentsAllowed'], DOCUMENT_SCHEMA_NS, 'comments')

    commentsAPIv2 = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentsAPIv2'], DOCUMENT_SCHEMA_NS,
        'comments_api_v2')

    commentSectionEnable = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['commentSectionEnable'],
        DOCUMENT_SCHEMA_NS, 'show_commentthread')

    dailyNewsletter = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['dailyNewsletter'], DOCUMENT_SCHEMA_NS, 'DailyNL')

    channels = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['channels'], DOCUMENT_SCHEMA_NS, 'channels',
        use_default=True)

    product = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['product'], 'http://namespaces.zeit.de/CMS/workflow',
        'product-id')

    storystreams = zeit.cms.content.dav.DAVProperty(
        ICommonMetadata['storystreams'], DOCUMENT_SCHEMA_NS,
        'storystreams', use_default=True)

    banner_outer = zeit.cms.content.DAVProperty(
        ICommonMetadata['banner_outer'], DOCUMENT_SCHEMA_NS, 'banner_outer',
        use_default=True)


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
