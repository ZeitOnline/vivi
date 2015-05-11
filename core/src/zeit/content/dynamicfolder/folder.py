# coding: utf8
from StringIO import StringIO
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import jinja2
import lxml.ElementInclude
import lxml.objectify
import persistent
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.connector.interfaces
import zeit.content.dynamicfolder.interfaces
import zope.cachedescriptors.property
import zope.container.contained
import zope.interface


def unique_id_loader(href, parse, encoding=None):
    """Resolves uniqueIds during XIncludes.

    When performing XInclude via lxml.ElementInclude.include, the href
    attribute is normally resolved as a URL. Since we reference data on the
    DAV, we need to resolve the href attribute using ICMSContent, which will
    return the DAV content.

    """
    data = zeit.connector.interfaces.IResource(
        zeit.cms.interfaces.ICMSContent(href)).data.read()
    if parse == "xml":
        return lxml.objectify.fromstring(data)
    return data


class VirtualProperties(grok.Adapter, dict):
    """Properties for virtual content. Actually returns no properties."""

    grok.context(zeit.content.dynamicfolder.interfaces.IVirtualContent)
    grok.implements(zeit.connector.interfaces.IWebDAVProperties)

    def __repr__(self):
        return object.__repr__(self)


class DynamicFolderBase(object):
    """Base class for the dynamic folder that holds all attributes.

    A base class is used to differentiate between repository and workingcopy.

    """

    zope.interface.implements(
        zeit.content.dynamicfolder.interfaces.IDynamicFolder)

    zeit.cms.content.dav.mapProperties(
        zeit.content.dynamicfolder.interfaces.IDynamicFolder,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('config_file',))


class RepositoryDynamicFolder(
        DynamicFolderBase,
        zeit.cms.repository.folder.Folder):
    """Inside the repository the dynamic folder can contain children."""

    zope.interface.implements(
        zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)

    def __getitem__(self, key):
        """Overwrite to return VirtualContent object for virtual content.

        Cannot use super, since we need to wrap getUncontainedContent with
        try/except. If the item was not found, create a virtual content and
        write basic information on it.

        """
        unique_id = self._get_id_for_name(key)
        __traceback_info__ = (key, unique_id)
        try:
            content = self.repository.getUncontainedContent(unique_id)
        except KeyError:
            content = self._create_virtual_content(key)
            self.repository.uncontained_content[unique_id] = content
        zope.interface.alsoProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)
        return zope.container.contained.contained(
            content, self, content.__name__)

    @zope.cachedescriptors.property.Lazy
    def cp_template(self):
        template_file = self.config.head.cp_template.text
        return jinja2.Template(
            zeit.connector.interfaces.IResource(
                zeit.cms.interfaces.ICMSContent(template_file)).data.read())

    def _create_virtual_content(self, key):
        resource = zeit.connector.resource.Resource(
            id=self._get_id_for_name(key),
            name=key,
            # XXX Make type configurable (<attribute> in the cp_template?).
            type='centerpage-2009',
            data=StringIO(self.cp_template.render(
                **self.virtual_content[key]['attrib'])),
            # XXX Convert <attribute>s of cp_template to DAV properties?
            properties={},
        )
        content = zeit.cms.interfaces.ICMSContent(resource)
        # Setting __name__ is normally done by
        # zeit.cms.repository.Repository._get_uncontained_copy().
        content.__name__ = resource.__name__
        zope.interface.alsoProvides(
            content, zeit.content.dynamicfolder.interfaces.IVirtualContent)
        return content

    @zope.cachedescriptors.property.Lazy
    def config(self):
        """Read virtual content from XML files and return as dict."""
        config = lxml.objectify.fromstring(zeit.connector.interfaces.IResource(
            self.config_file).data.read())
        lxml.ElementInclude.include(config, unique_id_loader)
        return config

    @zope.cachedescriptors.property.Lazy
    def virtual_content(self):
        """Read virtual content from XML files and return as dict."""
        contents = {}
        for child in self.config.body.getchildren():
            for letter in child.getchildren():
                for tag in letter.getchildren():
                    key = tag.get('url_value')
                    contents[key] = {'attrib': tag.attrib, 'text': tag.text}
        return contents

    @property
    def _local_unique_map(self):
        """Overwrite to add virtual content from XML.

        This property is used by all container methods, e.g. values, keys etc.

        The base implementation of the property has a side effect: It stores
        the data when retrieving the first time. Since we do not know whether
        the virtual content was already attached, we need to do it on every
        call, i.e. we cannot reuse the storing mechanism.

        """
        contents = super(RepositoryDynamicFolder, self)._local_unique_map
        result = self.virtual_content.copy()
        result.update(contents)
        return result


class LocalDynamicFolder(
        DynamicFolderBase,
        persistent.Persistent,
        zope.container.contained.Contained):
    """Inside the workingcopy the folder only holds attributes, no children."""

    zope.interface.implements(
        zeit.content.dynamicfolder.interfaces.ILocalDynamicFolder)


class DynamicFolderType(zeit.cms.repository.folder.FolderType):
    """Definition of the folder type. Creates a repository object."""

    factory = RepositoryDynamicFolder
    interface = zeit.content.dynamicfolder.interfaces.IDynamicFolder
    type = 'dynamic-collection'
    title = _('Dynamic Folder')
    addform = zeit.cms.type.SKIP_ADD


@grok.adapter(zeit.content.dynamicfolder.interfaces.IDynamicFolder)
@grok.implementer(zeit.content.dynamicfolder.interfaces.ILocalDynamicFolder)
def local_dynamic_folder_factory(context):
    local = LocalDynamicFolder()
    local.uniqueId = context.uniqueId
    local.__name__ = context.__name__
    zeit.connector.interfaces.IWebDAVWriteProperties(local).update(
        zeit.connector.interfaces.IWebDAVReadProperties(
            zope.security.proxy.getObject(context)))
    return local
