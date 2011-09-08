# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010 gocept gmbh & co. kg
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
import zeit.cms.content.property


class RSSBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IRSSBlock,
        zope.container.interfaces.IContained)

    max_items = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'max_items', zeit.content.cp.interfaces.IRSSBlock['max_items'])

    teaser_image = zeit.cms.content.property.SingleResource(
        '.teaser_image',
        xml_reference_name='image', attributes=('base-id', 'src'))

    feed_icon = zeit.cms.content.property.SingleResource(
        '.feed_icon',
        xml_reference_name='image', attributes=('base-id', 'src'))

    show_supertitle = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'show_supertitle',
        zeit.content.cp.interfaces.IRSSBlock['show_supertitle'])

    time_format = zeit.cms.content.property.ObjectPathAttributeProperty(
        '.', 'time_format',
        zeit.content.cp.interfaces.IRSSBlock['time_format'])

    def __init__(self, context, xml):
        super(RSSBlock, self).__init__(context, xml)
        if not self.xml.getchildren():
            self.xml.append(lxml.objectify.E.dummy_include())
        for field in ['max_items', 'show_supertitle', 'time_format']:
            if getattr(self, field) is None:
                setattr(self, field,
                        zeit.content.cp.interfaces.IRSSBlock[field].default)

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


zeit.content.cp.blocks.block.register_element_factory(
    [zeit.content.cp.interfaces.IInformatives,
    zeit.content.cp.interfaces.ITeaserBar], 'rss', _('RSS block'))
