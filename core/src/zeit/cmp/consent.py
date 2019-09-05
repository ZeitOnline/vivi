import grokcore.component as grok
import zeit.cmp.interfaces
import zeit.cms.content.dav


@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(zeit.cms.content.dav.DAVPropertiesAdapter):

    zeit.cms.content.dav.mapProperties(
        zeit.cmp.interfaces.IConsentInfo,
        u"http://namespaces.zeit.de/CMS/cmp",
        ('has_thirdparty', 'thirdparty_vendors',), use_default=True)
