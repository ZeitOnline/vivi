# coding: utf8
from StringIO import StringIO
from zeit.cms.i18n import MessageFactory as _
import copy
import grokcore.component as grok
import jinja2
import lxml.objectify
import persistent
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.connector.interfaces
import zeit.content.dynamicfolder.interfaces
import zope.app.locking.interfaces
import zope.container.contained
import zope.interface
import zope.security.proxy


class VirtualProperties(grok.Adapter, dict):
    """Properties for virtual content. Actually returns no properties."""

    grok.context(zeit.content.dynamicfolder.interfaces.IVirtualContent)
    grok.implements(zeit.connector.interfaces.IWebDAVProperties)

    def __repr__(self):
        return object.__repr__(self)


class DynamicFolderBase(persistent.Persistent,
                        zope.container.contained.Contained):
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
        except KeyError as error:
            if key not in self.virtual_content:
                raise error
            content = self._create_virtual_content(key)
            self.repository.uncontained_content[unique_id] = content
        zope.interface.alsoProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)
        return zope.container.contained.contained(
            content, self, content.__name__)

    @property
    def cp_template(self):
        if not hasattr(self, '_v_cp_template'):
            template_file = self.config.head.cp_template.text
            self._v_cp_template = jinja2.Template(
                zeit.connector.interfaces.IResource(
                    zeit.cms.interfaces.ICMSContent(
                        template_file)).data.read(),
                autoescape=True, extensions=['jinja2.ext.autoescape'])
        return self._v_cp_template

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
        # XXX Make type configurable (by using virtual DAV properties).
        zope.interface.alsoProvides(
            content, zeit.content.cp.interfaces.ICP2015)
        return content

    @property
    def config(self):
        """Read virtual content from XML files and return as dict.

        Supports the following include syntax:
          <include
            href="http://xml.zeit.de/path/to/file"
            xpointer="//some_xpath[@expression='goes here']"
            />

        We'd love to use xi:include for this, but lxml.ElementInclude (which
        allows overriding URL resolution) does not support xpointer, sigh.

        """
        if not self.config_file:
            return None

        if not hasattr(self, '_v_config'):
            config = lxml.objectify.fromstring(
                zeit.connector.interfaces.IResource(
                self.config_file).data.read())
            for include in config.xpath('//include'):
                parent = include.getparent()
                index = parent.index(include)
                parent.remove(include)
                for i, node in enumerate(self._resolve_include(include)):
                    parent.insert(index + i, node)
            self._v_config = config
        return self._v_config

    @staticmethod
    def _resolve_include(include):
        data = zeit.connector.interfaces.IResource(
            zeit.cms.interfaces.ICMSContent(include.get('href'))).data.read()
        document = lxml.objectify.fromstring(data)
        if include.get('xpointer'):
            return document.xpath(include.get('xpointer'))
        else:
            return [document]

    @property
    def virtual_content(self):
        """Read virtual content from XML files and return as dict."""
        if self.config is None:
            return {}

        if not hasattr(self, '_v_virtual_content'):
            contents = {}
            key_getter = self.config.body.get('key', 'text()')
            for entry in self.config.body.getchildren():
                key = unicode(entry.xpath(key_getter)[0])
                contents[key] = {'attrib': entry.attrib, 'text': entry.text}
            self._v_virtual_content = contents

        return self._v_virtual_content

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


class LocalDynamicFolder(DynamicFolderBase):
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


@grok.adapter(zeit.content.dynamicfolder.interfaces.IVirtualContent)
@grok.implementer(zeit.cms.checkout.interfaces.ILocalContent)
def virtual_local_content(context):
    # We cannot use IRepository.getCopyOf() to produce a copy of
    # IVirtualContent, so we need to do it ourselves.
    # Note: Our return value must not be security-wrapped (with getCopyOf()
    # that works out automatically).
    content = copy.copy(zope.security.proxy.getObject(context))
    zope.interface.alsoProvides(
        content, zeit.cms.workingcopy.interfaces.ILocalContent)
    zope.interface.noLongerProvides(
        content, zeit.cms.repository.interfaces.IRepositoryContent)
    return content


@grok.adapter(zeit.content.dynamicfolder.interfaces.IVirtualContent)
@grok.implementer(zope.app.locking.interfaces.ILockable)
def virtual_lockable(context):
    # Locking works on actual DAV objects, so we'd have to do a complete
    # re-implementation for virtual content. Since that's probably not worth
    # the effort, we simply make IVirtualContent not lockable.
    return None
