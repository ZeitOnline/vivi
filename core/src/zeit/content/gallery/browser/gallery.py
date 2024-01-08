import zope.component
import zope.interface
import zope.security

import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.repository.interfaces
import zeit.content.gallery.interfaces
import zeit.content.image.browser.image


@zope.component.adapter(
    zeit.cms.repository.interfaces.IFolder, zeit.content.gallery.interfaces.IGalleryFolderSource
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def gallery_folder_browse_location(context, source):
    """Gallery browse location

    this is the image browse location + '/bildergalerien'

    """
    image_source = zope.component.getUtility(
        zeit.cms.content.interfaces.ICMSContentSource, name='images'
    )
    image_folder = zope.component.queryMultiAdapter(
        (context, image_source), zeit.cms.browser.interfaces.IDefaultBrowsingLocation
    )
    gallery_folder = image_folder.get('bildergalerien')
    if gallery_folder is None:
        gallery_folder = image_folder
    return gallery_folder


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGallery, zeit.content.gallery.interfaces.IGalleryFolderSource
)
@zope.interface.implementer(zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def gallery_browse_location(context, source):
    return zope.component.queryMultiAdapter(
        (context.__parent__, source), zeit.cms.browser.interfaces.IDefaultBrowsingLocation
    )


class MetadataPreview(zeit.content.image.browser.image.MetadataPreview):
    def __init__(self, context, request):
        super().__init__(context.image, request)


class Index(zeit.cms.browser.view.Base):
    def __call__(self):
        views = ('overview.html', 'view.html')
        for name in views:
            view = zope.component.getMultiAdapter((self.context, self.request), name=name)
            if zope.security.canAccess(view, '__call__'):
                return self.redirect(self.url(view))
        raise zope.security.interfaces.Unauthorized()
