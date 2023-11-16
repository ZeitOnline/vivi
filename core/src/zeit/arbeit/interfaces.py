# -*- coding: utf-8 -*-

import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.cms.repository.interfaces
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.infobox.interfaces


class IZARSection(zeit.cms.section.interfaces.ISection):
    pass


class IZARContent(zeit.cms.interfaces.ICMSContent, zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZARFolder(
    zeit.cms.repository.interfaces.IFolder, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZARArticle(
    zeit.content.article.interfaces.IArticle, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZARCenterPage(
    zeit.content.cp.interfaces.ICenterPage, zeit.cms.section.interfaces.ISectionMarker
):
    pass


class IZARInfobox(
    zeit.content.infobox.interfaces.IInfobox, zeit.cms.section.interfaces.ISectionMarker
):
    pass
