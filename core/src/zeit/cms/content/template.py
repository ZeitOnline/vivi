# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent

import zope.securitypolicy.interfaces

import zope.app.container.btree
import zope.app.container.contained
import zope.app.security.settings

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


class TemplateManagerContainer(zope.app.container.btree.BTreeContainer):
    """Container which holds all template managers."""

    zope.interface.implements(
        zeit.cms.content.interfaces.ITemplateManagerContainer)


class TemplateManager(zope.app.container.btree.BTreeContainer):
    """Manages templates for a content type."""

    zope.interface.implements(zeit.cms.content.interfaces.ITemplateManager)


class Template(zope.app.container.contained.Contained,
               persistent.Persistent):
    """A template for xml content types."""

    zope.interface.implements(zeit.cms.content.interfaces.ITemplate)

    xml = None
    title = None


class TemplateWebDAVProperties(zeit.connector.resource.WebDAVProperties):
    """Special template properties with different security."""


@zope.annotation.factory
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webDAVPropertiesFactory():
    return TemplateWebDAVProperties()
