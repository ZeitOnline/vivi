import zope.schema

from zeit.cms.admin.interfaces import IAdjustSemanticPublish
from zeit.cms.checkout.helper import checked_out
from zeit.cms.content.interfaces import ICommonMetadata
from zeit.cms.workflow.interfaces import IPublishInfo
from zeit.content.image.interfaces import IImages
from zeit.content.link.link import Link
import zeit.cms.config
import zeit.cms.interfaces


def create(content, uniqueId):
    """Creates a Link object at `uniqueId` that links to the given `content`
    object, and copies its ICommonMetadata values.
    """
    path, name = uniqueId.rsplit('/', 1)
    container = zeit.cms.interfaces.ICMSContent(path + '/')
    container[name] = Link()
    link = container[name]

    with checked_out(link, temporary=False) as co:
        _copy_values(content, co)
        co.ressort = 'Administratives'
        co.url = content.uniqueId.replace(
            zeit.cms.interfaces.ID_NAMESPACE,
            zeit.cms.config.required('zeit.cms', 'live-prefix'),
        )
    _adjust_workflow(content, link)
    return link


def _copy_values(source, target):
    for iface in [ICommonMetadata, IImages]:
        src = iface(source)
        tgt = iface(target)
        for name, field in zope.schema.getFields(iface).items():
            __traceback_info__ = (field,)
            if name in SKIP_FIELDS:
                continue
            if field.readonly:
                continue
            value = field.get(src)
            if value != field.missing_value and value != field.default:
                field.set(tgt, value)


SKIP_FIELDS = {'channels', 'keywords', 'serie', 'ressort', 'sub_ressort'}


def _adjust_workflow(source, target):
    source_pub = IPublishInfo(source)
    target_pub = IAdjustSemanticPublish(target)
    target_pub.adjust_first_released = source_pub.date_first_released
    target_pub.adjust_semantic_publish = source_pub.date_last_published_semantic
    IPublishInfo(target).urgent = True
