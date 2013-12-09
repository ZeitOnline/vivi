# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.interfaces
import zeit.cms.section.interfaces


class IZMOSection(zeit.cms.section.interfaces.ISection):
    pass


class IZMOContent(
        zeit.cms.interfaces.ICMSContent,
        zeit.cms.section.interfaces.ISectionMarker):
    pass
