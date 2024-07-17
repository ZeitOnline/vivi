import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.config
import zeit.cms.content.contentsource
import zeit.cms.interfaces


class RelatableContentSource(zeit.cms.content.contentsource.CMSContentSource):
    def get_check_interfaces(self):
        types = zeit.cms.config.get('zeit.cms', 'relatable-content-types', '*')
        if types == '*':
            return super().get_check_interfaces()
        result = []
        for name in types.split():
            iface = zope.dottedname.resolve.resolve(name)
            if not zeit.cms.interfaces.ICMSContentType.providedBy(iface):
                raise TypeError('%r is not a CMS content type' % iface)
            result.append(iface)
        return result


relatableContentSource = RelatableContentSource()


class IRelatedContent(zope.interface.Interface):
    """Relate other content."""

    related = zope.schema.Tuple(
        title=_('Related content'),
        description=_('Objects that are related to this object.'),
        default=(),
        required=False,
        value_type=zope.schema.Choice(source=relatableContentSource),
    )
