# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.content.contentsource
import zeit.cms.interfaces
import zope.interface
import zope.schema


class RelatableContentSource(zeit.cms.content.contentsource.CMSContentSource):

    def get_check_interfaces(self):
        conf = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        types = conf.get('relatable-content-types', '*')
        if types == '*':
            return super(RelatableContentSource, self).get_check_interfaces()
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
        title=_("Related content"),
        description=_("Objects that are related to this object."),
        default=(),
        required=False,
        value_type=zope.schema.Choice(source=relatableContentSource))
