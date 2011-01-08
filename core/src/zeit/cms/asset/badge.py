# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import lxml.objectify
import zeit.cms.asset.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.property
import zeit.cms.content.xmlsupport
import zope.proxy


class Badges(zeit.cms.content.dav.DAVPropertiesAdapter,
             zeit.cms.content.xmlsupport.Persistent):

    grokcore.component.implements(zeit.cms.asset.interfaces.IBadges)
    grokcore.component.context(zeit.cms.content.interfaces.IXMLContent)

    badges = zeit.cms.content.property.SimpleMultiProperty(
        '.head.badges.badge', result_type=frozenset, sorted=sorted)

    @property
    def xml(self):
        return self.context.xml

    def _Persistent__get_persistent(self):
        context = getattr(self, 'context', None)
        return zope.proxy.removeAllProxies(context)


class MetadataUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):

    target_iface = zeit.cms.asset.interfaces.IBadges

    def update_with_context(self, entry, badges):
        if badges.badges:
            badges = [lxml.objectify.E.badge(badge)
                      for badge in sorted(badges.badges)]
            badges = lxml.objectify.E.badges(*badges)
            entry[badges.tag] = badges
        else:
            badges = entry.find('badges')
            if badges is not None:
                entry.remove(badges)
