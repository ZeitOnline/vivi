import persistent
import zc.sourcefactory.basic
import zeit.cms.content.interfaces
import zeit.connector.resource
import zope.container.btree
import zope.container.contained
import zope.interface


class BasicTemplateSourceFactory(zc.sourcefactory.basic.BasicSourceFactory):
    def getValues(self):
        manager = zope.component.getUtility(
            zeit.cms.content.interfaces.ITemplateManager, name=self.template_manager
        )
        return manager.values()

    def getTitle(self, obj):
        return obj.title


def BasicTemplateSource(template_manager):
    source = BasicTemplateSourceFactory()
    source.factory.template_manager = template_manager
    return source


@zope.interface.implementer(zeit.cms.content.interfaces.ITemplateManagerContainer)
class TemplateManagerContainer(zope.container.btree.BTreeContainer):
    """Container which holds all template managers."""


@zope.interface.implementer(zeit.cms.content.interfaces.ITemplateManager)
class TemplateManager(zope.container.btree.BTreeContainer):
    """Manages templates for a content type."""


@zope.interface.implementer(zeit.cms.content.interfaces.ITemplate)
class Template(zope.container.contained.Contained, persistent.Persistent):
    """A template for xml content types."""

    xml = None
    title = None


class TemplateWebDAVProperties(zeit.connector.resource.WebDAVProperties):
    """Special template properties with different security."""


@zope.annotation.factory
@zope.component.adapter(zeit.cms.content.interfaces.ITemplate)
@zope.interface.implementer(zeit.connector.interfaces.IWebDAVProperties)
def webDAVPropertiesFactory():
    return TemplateWebDAVProperties()
