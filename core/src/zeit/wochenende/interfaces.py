# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.cms.repository.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces


class IZWESection(zeit.cms.section.interfaces.ISection):
    pass


class IZWEContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZWEFolder(
    zeit.cms.repository.interfaces.IFolder, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZWECenterPage(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.section.interfaces.ISectionMarker
):
    pass
