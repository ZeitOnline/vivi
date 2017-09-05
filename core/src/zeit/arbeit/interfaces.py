# -*- coding: utf-8 -*-

from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.content.sources
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.infobox.interfaces
import zope.schema


class IZARSection(zeit.cms.section.interfaces.ISection):
    pass


class IZARContent(
        zeit.cms.interfaces.ICMSContent,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZARFolder(
        zeit.cms.repository.interfaces.IFolder,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZARArticle(
        zeit.content.article.interfaces.IArticle,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZARCenterPage(
        zeit.content.cp.interfaces.ICenterPage,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


class IZARInfobox(
        zeit.content.infobox.interfaces.IInfobox,
        zeit.cms.section.interfaces.ISectionMarker):
    pass


JOBBOX_TICKER_SOURCE = zeit.cms.content.sources.JobboxTickerSource(
    zeit.content.article.interfaces.IArticle)


class IJobboxTicker(zeit.edit.interfaces.IBlock):

    jobbox_ticker = zope.schema.Choice(
        title=_('Jobbox ticker'),
        required=True,
        source=JOBBOX_TICKER_SOURCE)
