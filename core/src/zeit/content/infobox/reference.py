# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.cms.content.dav
import zeit.content.infobox.interfaces


class InfoboxReference(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.implements(
        zeit.content.infobox.interfaces.IInfoboxReference)

    infobox = zeit.cms.content.dav.DAVProperty(
        zeit.content.infobox.interfaces.IInfoboxReference['infobox'],
        'http://namespaces.zeit.de/CMS/document', 'artbox_info')
