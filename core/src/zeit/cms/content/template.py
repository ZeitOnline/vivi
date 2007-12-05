# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent

import zope.app.container.btree
import zope.app.container.contained

import zc.sourcefactory.basic

import zeit.cms.content.interfaces


class BasicTemplateSource(zc.sourcefactory.basic.BasicSourceFactory):

    template_manager = None

    def __init__(self):
        if self.template_manager is None:
            raise NotImplementedError("`template_manager` needs to be specified")
        super(BasicTemplateSource, self).__init__()

    def getValues(self):
        manager = zope.component.getUtility(
            zeit.cms.content.interfaces.ITemplateManager,
            name=self.template_manager)
        return manager.values()

    def getTitle(self, obj):
        return obj.title


class TemplateManager(zope.app.container.btree.BTreeContainer):

    zope.interface.implements(zeit.cms.content.interfaces.ITemplateManager)


class Template(zope.app.container.contained.Contained,
               persistent.Persistent):

    zope.interface.implements(zeit.cms.content.interfaces.ITemplate)

    xml = None
    title = None
