# -*- coding: utf-8 -*-

from zeit.cms.application import CONFIG_CACHE
from zeit.cms.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.cms.section.interfaces
import zeit.cms.repository.interfaces
import zeit.cms.content.sources
import zeit.content.article.interfaces
import zeit.content.cp.interfaces
import zeit.content.infobox.interfaces
import zope.schema
import collections


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


class JobboxTicker(zeit.cms.content.sources.AllowedBase):

    def __init__(self, id, title, available, feed_url, landing_url, teaser):
        super(JobboxTicker, self).__init__(id, title, available)
        self.feed_url = feed_url
        self.landing_url = landing_url
        self.teaser = teaser

    def is_allowed(self, context):
        article = zeit.content.article.interfaces.IArticle(context, None)
        return super(JobboxTicker, self).is_allowed(article)


class JobboxTickerSource(
        zeit.cms.content.sources.ObjectSource,
        zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.arbeit'
    config_url = 'article-jobbox-ticker-source'
    attribute = 'id'

    @CONFIG_CACHE.cache_on_arguments()
    def _values(self):
        tree = self._get_tree()
        result = collections.OrderedDict()
        for node in tree.iterchildren('*'):
            g = node.get
            id = node.get(self.attribute)
            result[id] = JobboxTicker(
                id, g('title'), g('available', None),
                g('feed_url', None), g('landing_url', None), g('teaser', None))
        return result


JOBBOX_TICKER_SOURCE = JobboxTickerSource()


class IJobboxTicker(zeit.edit.interfaces.IBlock):

    # For editing
    jobbox = zope.schema.Choice(
        title=_('Jobbox ticker'),
        required=True,
        source=JOBBOX_TICKER_SOURCE)
