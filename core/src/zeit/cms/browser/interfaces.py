
import gocept.form.interfaces
import zope.interface
import zope.interface.common.mapping
import zope.publisher.interfaces.browser
import zope.schema
import zope.viewlet.interfaces


class ICMSStyles(zope.publisher.interfaces.browser.IBrowserRequest):
    """Styles (CSS) for the CMS."""


class ICMSOldStyles(zope.publisher.interfaces.browser.IBrowserRequest):
    """Old Styles (CSS) for the CMS (yellow tabs etc.)."""


class ICMSLayer(zope.publisher.interfaces.browser.IBrowserRequest):
    """Master Layer for CMS skin"""


class IRepositoryLayer(ICMSLayer):
    """Layer for repository content."""


class IWorkingcopyLayer(ICMSLayer):
    """Layer for workingcopy content."""


class IGlobalSearchLayer(zope.publisher.interfaces.browser.IBrowserRequest):
    """A for UI elements which require a search to be available.

    This layer is exists to migrate elements to use the global search once it
    becomes available (#6380).

    """


class IAdditionalLayer(zope.interface.Interface):
    """Adapter to retrieve an additional layer for the given object.

    Used to add an additional layer to the request, depending on the URL. More
    specifically, the first container after root is inspected and depending on
    if it is "repository" or "workingcopy", the interface IRepositoryLayer or
    IWorkingcopyLayer is added.

    """


class ICMSTestingSkin(ICMSStyles,
                      ICMSLayer,
                      zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """Layer/Skin which is only used in tests."""


class ICMSSkin(ICMSStyles,
               ICMSLayer,
               gocept.form.interfaces.IJSValidationLayer,
               zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """CMS skin"""


class IGlobalInformation(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the right header area."""


class IGlobalViews(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for global menu."""


class ISecondaryGlobalViews(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for secondary items in the global menu."""


class IContextActions(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for actions menu."""


class IContextViews(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for views menu."""


class ISecondaryContextActions(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for less important actions (two clicks away.)"""


class ISidebar(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the sidebar"""


class IMetadataPreview(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the metadata preview."""


class IListRepresentation(zope.interface.Interface):
    """List representation of content objects"""

    __name__ = zope.interface.Attribute('File name')
    uniqueId = zope.interface.Attribute('Unique ID in repository.')
    url = zope.schema.URI(title='URL to the object in the CMS.')
    context = zope.interface.Attribute('Represended object.')
    type = zope.interface.Attribute('Resource type (if known).')

    title = zope.interface.Attribute('Content title')
    author = zope.interface.Attribute('Author')
    ressort = zope.interface.Attribute('Ressort')
    searchableText = zope.interface.Attribute('Index used to search the list')
    page = zope.schema.Int(title='Page in paper')
    volume = zope.schema.Int(title='Volume')
    year = zope.schema.Int(title='Year')

    modifiedBy = zope.interface.Attribute('Datetime of last modification')

    modifiedOn = zope.interface.Attribute(
        'datetime of last modification.')

    createdOn = zope.interface.Attribute(
        'datetime of creation date.')


class ITreeState(zope.interface.common.mapping.IMapping):
    """Saves the tree state for various trees."""


class ITree(zope.interface.Interface):
    """Tree rendering."""

    root = zope.interface.Attribute("The root of the tree.")

    def expandNode(self, id):
        """Expand the node identified by id."""

    def collapseNode(self, id):
        """Collapse the node identified by id."""


class IPanelState(zope.interface.Interface):
    """Remembers the state of panel folding.

    Calling foldPandel(...) results in the panel to be folded uppon the next
    request. Actual inline folding of a panel in the browser needs to be done
    with java script directly in the browser.

    """

    def folded(panel):
        """Return if `panel` is folded."""

    def foldPanel(panel):
        """Fold `pandel`."""

    def unfoldPanel(panel):
        """Unfold `pandel`."""


class ICMSUserPreferences(zope.interface.Interface):

    sidebarFolded = zope.schema.Bool(
        title='Sidebar folded?',
        default=False)


class IDefaultBrowsingLocation(zope.interface.Interface):
    """Object representing the default browse location for object browser.

    For instance if looking for images the default location could be the image
    folder.

    """


class IPreviewObject(zope.interface.Interface):
    """Adapter to find an object to preview an asset.

    When an asset (like a channel) needs to be previewed it often cannot be
    shown directly but another object which uses the asset needs to be shown.

    Assets can register an adapter factor to IPreviewObject which must yield a
    previewable object.

    """


class IPreviewURL(zope.interface.Interface):
    """Adapter to get the preview URL for an object.

    Returns the URL as a string.
    """


class IEditViewName(zope.interface.Interface):
    """Adapter to get the edit view name for context and display view name.

    edit_view_name = getAdapter(
        a_content_object,
        IEditViewName, name='view.html')

    """


class IDisplayViewName(zope.interface.Interface):
    """Adapter to get the display view name for context and edit view name.

    display_view_name = getAdapter(
        a_content_object,
        IDisplayViewName, name='edit.html')

    """


class ISourceQueryURL(zope.interface.Interface):
    """Adapts an IAutocompleteSource and request to a string, which is the URL
    through which this source can be queried (at the moment: using the jqueryui
    autocomplete JSON protocol).

    XXX Using a traverser to get to the source (How? Dotted name and require
    sources to be singletons?) and a well-known view name on the source instead
    of on the site would be much cleaner.

    """
