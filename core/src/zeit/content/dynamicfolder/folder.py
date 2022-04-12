# coding: utf8
from io import BytesIO
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.content.contentuuid import ContentUUID
from zeit.content.dynamicfolder.interfaces import IVirtualContent
import copy
import grokcore.component as grok
import hashlib
import jinja2
import lxml.etree
import lxml.objectify
import persistent
import six
import six.moves.urllib.parse
import uuid
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.repository.folder
import zeit.cms.repository.interfaces
import zeit.connector.interfaces
import zeit.connector.resource
import zeit.content.dynamicfolder.interfaces
import zeit.workflow.dependency
import zope.app.locking.interfaces
import zope.container.contained
import zope.interface
import zope.security.proxy


@zope.interface.implementer(
    zeit.content.dynamicfolder.interfaces.IDynamicFolder)
class DynamicFolderBase(object):
    """Base class for the dynamic folder that holds all attributes.

    A base class is used to differentiate between repository and workingcopy.

    """

    zeit.cms.content.dav.mapProperties(
        zeit.content.dynamicfolder.interfaces.IDynamicFolder,
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        ('config_file',))


@zope.interface.implementer(
    zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)
class RepositoryDynamicFolder(
        DynamicFolderBase,
        zeit.cms.repository.folder.Folder):
    """Inside the repository the dynamic folder can contain children."""

    def __getitem__(self, key):
        """Overwrite to return VirtualContent object for virtual content.

        Cannot use super, since we need to wrap getContent with
        try/except. If the item was not found, create a virtual content and
        write basic information on it.

        """
        unique_id = self._get_id_for_name(key)
        __traceback_info__ = (key, unique_id)
        try:
            content = self.repository._getContent(unique_id)
        except KeyError as error:
            if key not in self.virtual_content:
                raise error
            content = self._create_virtual_content(key)
            # XXX copy&paste from Repository._getContent().
            self.repository._add_marker_interfaces(content)
            self.repository._content[unique_id] = content
        return zope.container.contained.contained(
            content, self, content.__name__)

    def __delitem__(self, key):
        value = self.get(key)
        if value is not None and IVirtualContent.providedBy(value):
            return
        super(RepositoryDynamicFolder, self).__delitem__(key)

    @property
    def content_template(self):
        if not hasattr(self, '_v_content_template'):
            if self.content_template_file is None:
                return jinja2.Template('')
            self._v_content_template = jinja2.Template(
                zeit.connector.interfaces.IResource(
                    self.content_template_file).data.read().decode('utf-8'),
                autoescape=True, extensions=['jinja2.ext.autoescape'])
        return self._v_content_template

    @property
    def content_template_file(self):
        template_file = self.config.head.findtext('cp_template')
        return zeit.cms.interfaces.ICMSContent(template_file, None)

    def _create_virtual_content(self, key):
        body = self.content_template.render(
            **self.virtual_content[key]).encode('utf-8')
        properties = VirtualProperties.parse(body)
        resource = zeit.connector.resource.Resource(
            id=self._get_id_for_name(key),
            name=key,
            type=properties.get(
                ('type', 'http://namespaces.zeit.de/CMS/meta'),
                'centerpage-2009'),
            data=BytesIO(body),
            # Even though virtual content never touches the connector and thus
            # we have to override the IWebDAVProperties adapter, some parts of
            # the system use this, e.g. for reconstructing provided interfaces.
            properties=properties,
        )
        content = zeit.cms.interfaces.ICMSContent(resource)
        # Setting __name__ is normally done by Repository.getCopyOf().
        content.__name__ = resource.__name__
        zope.interface.alsoProvides(
            content, zeit.content.dynamicfolder.interfaces.IVirtualContent)
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
        NOTE: The included nodes are appended at the end of the parent element,
        not at the position of the <include> node (since that's twice as fast).

        """
        if not self.config_file:
            return None

        if not hasattr(self, '_v_config'):
            config = lxml.objectify.fromstring(
                zeit.connector.interfaces.IResource(
                    self.config_file).data.read())
            for include in config.xpath('//include'):
                parent = include.getparent()
                parent.remove(include)
                for node in self._resolve_include(include):
                    parent.append(node)
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
                key_match = entry.xpath(key_getter)
                if not key_match:
                    continue  # entry provides no key
                key = six.moves.urllib.parse.unquote(key_match[0])
                if isinstance(key, lxml.etree._ElementUnicodeResult):
                    # Dear lxml, why?
                    key = six.text_type(key)
                else:
                    key = six.ensure_text(key)
                contents[key] = dict(entry.attrib)  # copy
                contents[key]['text'] = entry.text
                contents[key]['__parent__'] = self
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


@zope.interface.implementer(
    zeit.content.dynamicfolder.interfaces.ILocalDynamicFolder)
class LocalDynamicFolder(DynamicFolderBase,
                         persistent.Persistent,
                         zope.container.contained.Contained):
    """Inside the workingcopy the folder only holds attributes, no children."""


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
        zeit.connector.interfaces.IWebDAVReadProperties(context))
    return local


@grok.adapter(zeit.content.dynamicfolder.interfaces.IVirtualContent)
@grok.implementer(zeit.cms.checkout.interfaces.ILocalContent)
def virtual_local_content(context):
    # We cannot use IRepository.getCopyOf() (like
    # zeit.cms.repository.checkout.default_local_content_adapter does) to
    # produce a copy of IVirtualContent, so we need to do it ourselves.
    # (Note: Our return value must not be security-wrapped; with getCopyOf()
    # that works out automatically).
    content = copy.copy(zope.security.proxy.getObject(context))
    repository_properties = zeit.connector.interfaces.IWebDAVReadProperties(
        context)

    zope.interface.alsoProvides(
        content, zeit.cms.workingcopy.interfaces.ILocalContent)
    zope.interface.noLongerProvides(
        content, zeit.cms.repository.interfaces.IRepositoryContent)

    zope.interface.noLongerProvides(
        content, zeit.content.dynamicfolder.interfaces.IVirtualContent)
    new_properties = zeit.connector.interfaces.IWebDAVWriteProperties(content)
    new_properties.update(repository_properties)

    return content


@grok.adapter(zeit.content.dynamicfolder.interfaces.IVirtualContent)
@grok.implementer(zope.app.locking.interfaces.ILockable)
def virtual_lockable(context):
    # Locking works on actual DAV objects, so we'd have to do a complete
    # re-implementation for virtual content. Since that's probably not worth
    # the effort, we simply make IVirtualContent not lockable.
    return None


class VirtualProperties(zeit.connector.resource.WebDAVProperties,
                        grok.Adapter):

    grok.context(zeit.content.dynamicfolder.interfaces.IVirtualContent)
    grok.provides(zeit.connector.interfaces.IWebDAVProperties)

    ID_PROPERTY = (ContentUUID.id.name, ContentUUID.id.namespace)

    def __init__(self, context):
        super(VirtualProperties, self).__init__()
        self.context = context
        self.update(self.parse(context.xml))
        self[self.ID_PROPERTY] = '{%s}' % uuid.UUID(
            hashlib.md5(context.uniqueId.encode('utf-8')).hexdigest()).urn

    # XXX zeit.cms.content.xmlsupport.PropertyToXMLAttribute violates
    # the contract by assuming that IWebDAVProperties of IRepositoryContent
    # also provides zeit.cms.content.liveproperty.LiveProperties methods.
    def is_writeable_on_checkin(self, name, namespace):
        return True

    @classmethod
    def parse(cls, body):
        if isinstance(body, (six.binary_type, six.text_type)):
            try:
                body = lxml.etree.fromstring(body)
            except lxml.etree.LxmlError:
                return {}
        return zeit.connector.filesystem.parse_properties(
            zope.security.proxy.getObject(body))


class ConfigDependency(zeit.workflow.dependency.DependencyBase):
    """Publishes the config and content template files along with the dynamic
    folder."""

    grok.context(zeit.content.dynamicfolder.interfaces.IDynamicFolder)
    grok.name('zeit.content.dynamicfolder.config')

    retract_dependencies = True

    def get_dependencies(self):
        result = []
        for name in ['config_file', 'content_template_file']:
            config = getattr(self.context, name)
            if config is not None:
                result.append(config)
        return result


class FolderDependencies(zeit.workflow.dependency.DependencyBase):

    grok.context(zeit.content.dynamicfolder.interfaces.IDynamicFolder)
    grok.name('zeit.cms.repository.folder')

    retract_dependencies = True

    def get_dependencies(self):
        return []
