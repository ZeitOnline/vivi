# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent

import zope.app.container.btree
import zope.app.container.contained

import zc.sourcefactory.basic

import zeit.cms.content.interfaces


class BasicTemplateSourceFactory(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        manager = zope.component.getUtility(
            zeit.cms.content.interfaces.ITemplateManager,
            name=self.template_manager)
        return manager.values()

    def getTitle(self, obj):
        return obj.title


def BasicTemplateSource(template_manager):
    source = BasicTemplateSourceFactory()
    source.factory.template_manager = template_manager
    return source


class TemplateManager(zope.app.container.btree.BTreeContainer):

    zope.interface.implements(zeit.cms.content.interfaces.ITemplateManager)


class Template(zope.app.container.contained.Contained,
               persistent.Persistent):

    zope.interface.implements(zeit.cms.content.interfaces.ITemplate)

    xml = None
    title = None
