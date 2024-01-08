import grokcore.component as grok

from zeit.cmp.interfaces import VENDOR_SOURCE
import zeit.cmp.interfaces
import zeit.cms.content.dav


class ConsentInfoBase:
    @property
    def thirdparty_vendors_cmp_ids(self):
        return tuple(VENDOR_SOURCE(self).attributes(x).get('cmp') for x in self.thirdparty_vendors)


@grok.implementer(zeit.cmp.interfaces.IConsentInfo)
class ConsentInfo(zeit.cms.content.dav.DAVPropertiesAdapter, ConsentInfoBase):
    zeit.cms.content.dav.mapProperties(
        zeit.cmp.interfaces.IConsentInfo,
        'http://namespaces.zeit.de/CMS/cmp',
        (
            'has_thirdparty',
            'thirdparty_vendors',
        ),
        use_default=True,
    )
