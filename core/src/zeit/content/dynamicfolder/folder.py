# coding: utf8
from zeit.cms.i18n import MessageFactory as _
import grokcore.component as grok
import lxml.ElementInclude
import lxml.etree
import persistent
import zeit.cms.browser.interfaces
import zeit.cms.browser.listing
import zeit.cms.content.dav
import zeit.cms.content.sources
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


class VirtualContent(object):
    """Represents content objects that are created on-the-fly.

    DynamicFolder displays content that is not present on the DAV, but defined
    via XML. To display those objects, they are created on-the-fly using this
    class.

    The content is virtual, since it will not be persisted on the DAV.

    Uses the same default values as defined in the schema of ICommonMetadata.

    """

    zope.interface.implements(
        zeit.content.dynamicfolder.interfaces.IVirtualContent)

    __name__ = None
    uniqueId = None
    year = None
    volume = None
    page = None
    ressort = None
    sub_ressort = None
    channels = []
    lead_candidate = True
    printRessort = u'n/a'
    authorships = []
    authors = []
    keywords = []
    serie = None
    copyrights = None
    supertitle = None
    byline = None
    title = None
    subtitle = None
    teaserTitle = None
    teaserText = None
    teaserSupertitle = None
    vg_wort_id = None
    dailyNewsletter = True
    commentsAllowed = True
    commentSectionEnable = True
    banner = True
    banner_id = None
    product = zeit.cms.content.sources.Product(u'ZEDE')
    product_text = None
    foldable = True
    minimal_header = False
    color_scheme = u'Redaktion'
    countings = True
    is_content = True
    breaking_news = False
    push_news = False
    in_rankings = True
    cap_title = None
    mobile_alternative = None
    deeplink_url = None
    breadcrumb_title = None
    rebrush_website_content = False


class VirtualContentListRepresentation(
        zeit.cms.browser.listing.CommonListRepresentation):
    """Wraps virtual content to display some attributes in the container view.

    Since VirtualContent implements ICommonMetadata, we can reuse
    CommonListRepresentation here.

    """

    zope.interface.implements(zeit.cms.browser.interfaces.IListRepresentation)
    zope.component.adapts(
        zeit.content.dynamicfolder.interfaces.IVirtualContent,
        zeit.cms.browser.interfaces.ICMSLayer)

    def _dc_date_helper(self, attribute):
        """Overwrite, since the virtual content does not implement the DC."""
        return None


class RepositoryDynamicFolder(
        DynamicFolderBase,
        zeit.cms.repository.folder.Folder):
    """Inside the repository the dynamic folder can contain children."""

    zope.interface.implements(
        zeit.content.dynamicfolder.interfaces.IRepositoryDynamicFolder)

    def create_virtual_content(self, key):
        content = VirtualContent()
        content.__name__ = key
        content.title = self.virtual_content[key]
        content.uniqueId = '/'.join(x.strip('/') for x in [self.uniqueId, key])
        return content

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
            content = self.create_virtual_content(key)
        zope.interface.alsoProvides(
            content, zeit.cms.repository.interfaces.IRepositoryContent)
        return zope.container.contained.contained(
            content, self, content.__name__)

    @zope.cachedescriptors.property.Lazy
    def virtual_content(self):
        """Read virtual content from XML files and return as dict."""
        config = lxml.objectify.fromstring(zeit.connector.interfaces.IResource(
            self.config_file).data.read())
        lxml.ElementInclude.include(config, unique_id_loader)

        contents = {}
        for child in config.find('body').getchildren():
            for letter in child.getchildren():
                for tag in letter.getchildren():
                    key = tag.get('url_value')
                    contents[key] = tag.get('lexical_value')
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
