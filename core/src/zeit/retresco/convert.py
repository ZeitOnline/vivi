from datetime import datetime
from zeit.cms.interfaces import ITypeDeclaration
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.image.interfaces import IImageMetadata
import grokcore.component as grok
import lxml.etree
import pytz
import zeit.cms.content.interfaces
import zeit.content.article.interfaces
import zeit.retresco.interfaces

MIN_DATE = datetime(1970, 1, 1, tzinfo=pytz.UTC)


def to_json(context):
    if not zeit.cms.content.interfaces.ICommonMetadata.providedBy(context):
        return None

    # XXX This probably needs to expand to something like zeit.solr.converter.
    doc = {
        'doc_id': zeit.cms.content.interfaces.IUUID(context).id,
        'url': context.uniqueId.replace(zeit.cms.interfaces.ID_NAMESPACE, '/'),
        'doc_type': getattr(ITypeDeclaration(context, None),
                            'type_identifier', 'unknown'),
        'title': context.title,
        'supertitle': context.supertitle,
        'teaser': context.teaserText,
        'body': lxml.etree.tostring(
            zeit.retresco.interfaces.IBody(context)),
        'section': context.ressort,
        # XXX date is required; what about unpublished content?
        'date': json_date(IPublishInfo(context).date_first_released
                          or MIN_DATE)
    }

    image = getattr(
        zeit.content.image.interfaces.IImages(context, None), 'image', None)
    if image is not None:
        doc['teaser_img_url'] = image.uniqueId.replace(
            zeit.cms.interfaces.ID_NAMESPACE, '/')
        doc['teaser_img_subline'] = IImageMetadata(image).caption

    doc['author'] = ', '.join([
        x.target.display_name for x in context.authorships])

    return doc


def json_date(date):
    return date.astimezone(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


@grok.adapter(zeit.cms.content.interfaces.IXMLRepresentation)
@grok.implementer(zeit.retresco.interfaces.IBody)
def default_body(context):
    # This is probably not very helpful.
    return context.xml


@grok.adapter(zeit.content.article.interfaces.IArticle)
@grok.implementer(zeit.retresco.interfaces.IBody)
def article_body(context):
    return context.xml.body
