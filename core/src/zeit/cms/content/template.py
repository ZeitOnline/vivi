# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import persistent

import zope.app.container.btree
import zope.app.container.contained

import zc.sourcefactory.basic

import zeit.cms.content.interfaces


class BasicTemplateSource(zc.sourcefactory.basic.BasicSourceFactory):

    template_type = None

    def __init__(self):
        if self.template_type is None:
            raise NotImplementedError("`template_type` needs to be specified")
        super(BasicTemplateSource, self).__init__()

    def getValues(self, context):
        manager = zope.component.getUtility(
            zeit.cms.content.interfaces.ITemplateManager,
            name=self.template_type)
        return manager.values()


class TemplateManager(zope.app.container.btree.BTreeContainer):

    zope.interface.implements(zeit.cms.content.interfaces.ITemplateManager)


class Template(zope.app.container.contained.Contained,
               persistent.Persistent):

    zope.interface.implements(zeit.cms.content.interfaces.ITemplate)

    xml = None
    title = None
