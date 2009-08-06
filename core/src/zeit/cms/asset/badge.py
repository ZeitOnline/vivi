# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.cms.asset.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.content.property


class Badges(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(zeit.cms.asset.interfaces.IBadges)
    grokcore.component.context(zeit.cms.content.interfaces.IXMLContent)

    badges = zeit.cms.content.property.SimpleMultiProperty(
        '.head.badges.badge', result_type=frozenset, sorted=sorted)

    @property
    def xml(self):
        return self.context.xml
