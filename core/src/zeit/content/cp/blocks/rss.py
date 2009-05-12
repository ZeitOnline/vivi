# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zope.container.interfaces
import zope.interface
import rwproperty
import lxml.objectify

class DummyFeed(object):

    uniqueId = '%sfoo' % zeit.cms.interfaces.ID_NAMESPACE

    def __init__(self, url):
        pass


class RSSBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IRSSBlock,
        zope.container.interfaces.IContained)

    def __init__(self, context, xml):
        super(RSSBlock, self).__init__(context, xml)
        if len(self.xml.getchildren()) == 0:
            self.xml.append(lxml.objectify.E.dummy_include())

    def create_include(self, url):
        include_maker = lxml.objectify.ElementMaker(
            annotate=False,
            namespace='http://www.w3.org/2003/XInclude',
            nsmap={'xi': 'http://www.w3.org/2003/XInclude'},
        )

        feed = FeedFactory(url)

        path = feed.uniqueId.replace(
            zeit.cms.interfaces.ID_NAMESPACE, '/var/cms/')

        return include_maker.include(
            include_maker.fallback('Feed nicht erreichbar.'),
            parse='xml',
            href=path)

    @rwproperty.setproperty
    def url(self, url):
        self.xml.set('url', url)
        self.xml.replace(self.xml.getchildren()[0], self.create_include(url))

    @rwproperty.getproperty
    def url(self):
        return self.xml.get('url')


RSSBlockFactory = zeit.content.cp.blocks.block.blockFactoryFactory(
    zeit.content.cp.interfaces.IRegion,
    RSSBlock, 'rssblock', _('RSS block'))

FeedFactory = DummyFeed
