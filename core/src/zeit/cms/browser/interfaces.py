# Copyright (c) 2006-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interfaces for CMS skin"""

import zope.interface.common.mapping
import zope.publisher.interfaces.browser
import zope.viewlet.interfaces
import zope.interface
import zope.schema

import gocept.form.interfaces


class ICMSLayer(zope.publisher.interfaces.browser.IBrowserRequest):
    """Master Layer for CMS skin"""


class ICMSTestingSkin(ICMSLayer,
                      zope.publisher.interfaces.browser.IBrowserRequest,
                      zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """Layer/Skin which is only used in tests."""


class ICMSSkin(ICMSLayer,
               gocept.form.interfaces.IJSValidationLayer,
               zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """CMS skin"""


class IGlobalInformation(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the right header area."""


class IGlobalViews(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for global menu."""


class IContextActions(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for actions menu."""


class ISidebar(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the sidebar"""


class IMetadataPreview(zope.viewlet.interfaces.IViewletManager):
    """Viewlets for the metadata preview."""


class IListRepresentation(zope.interface.Interface):
    """List representation of content objects"""

    __name__ = zope.interface.Attribute("File name")
    uniqueId = zope.interface.Attribute("Unique ID in repository.")
    url = zope.schema.URI(title=u"URL to the object in the CMs.")
    context = zope.interface.Attribute("Represended object.")
    type = zope.interface.Attribute(u"Resource type (if known).")

    title = zope.interface.Attribute("Content title")
    author = zope.interface.Attribute("Author")
    ressort = zope.interface.Attribute("Ressort")
    searchableText = zope.interface.Attribute("Index used to search the list")
    page = zope.schema.Int(title=u"Page in paper")
    volume = zope.schema.Int(title=u"Volume")
    year = zope.schema.Int(title=u"Year")

    workflowState = zope.interface.Attribute("Workflow State")

    modifiedBy = zope.interface.Attribute("Datetime of last modification")

    modifiedOn = zope.interface.Attribute(
        "datetime of last modification.")

    createdOn = zope.interface.Attribute(
        "datetime of creation date.")


class IImageRepresentation(zope.interface.Interface):
    """Image representation of content objects."""

    title = zope.interface.Attribute("Content title")
    thumbnailUrl = zope.interface.Attribute("Thumbnail url used for Preview")


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
        title=u"Sidebar folded?",
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
