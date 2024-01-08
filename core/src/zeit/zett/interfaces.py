# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.section.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.infobox.interfaces


class IZTTSection(zeit.cms.section.interfaces.ISection):
    pass


class IZTTContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZTTFolder(
    zeit.cms.repository.interfaces.IFolder, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZTTArticle(
    zeit.content.article.interfaces.IArticle, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZTTCenterPage(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.section.interfaces.ISectionMarker
):
    pass
