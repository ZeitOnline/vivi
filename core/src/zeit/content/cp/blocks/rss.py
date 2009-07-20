# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import thread
from zeit.content.cp.blocks.teaser import create_xi_include
from zeit.content.cp.i18n import MessageFactory as _
import lxml.objectify
import rwproperty
import zeit.cms.connector
import zeit.cms.content.adapter
import zeit.cms.content.xmlsupport
import zeit.cms.repository.interfaces
import zeit.content.cp.blocks.block
import zeit.content.cp.feed
import zeit.content.cp.interfaces
import zope.app.appsetup.product
import zope.component
import zope.container.interfaces
import zope.interface


class RSSBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IRSSBlock,
        zope.container.interfaces.IContained)

    def __init__(self, context, xml):
        super(RSSBlock, self).__init__(context, xml)
        if not self.xml.getchildren():
            self.xml.append(lxml.objectify.E.dummy_include())

    @rwproperty.setproperty
    def url(self, url):
        self.xml.set('url', url)
        self._p_changed = True
        self.xml.replace(self.xml.getchildren()[0],
                         create_xi_include(self.feed, '/feed/rss'))

    @rwproperty.getproperty
    def url(self):
        return self.xml.get('url')

    @property
    def feed(self):
        return zope.component.getUtility(
            zeit.content.cp.interfaces.IFeedManager).get_feed(self.url)


RSSBlockFactory = zeit.content.cp.blocks.block.elementFactoryFactory(
    zeit.content.cp.interfaces.IRegion, 'rss', _('RSS block'))
