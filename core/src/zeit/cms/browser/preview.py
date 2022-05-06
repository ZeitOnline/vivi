import urllib.parse
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.interfaces
import zope.app.appsetup.product


def prefixed_url(prefix, unique_id):
    """Given a prefix and a unique id, return preview URL.
    """
    if not unique_id.startswith(zeit.cms.interfaces.ID_NAMESPACE):
        raise ValueError("UniqueId doesn't start with correct prefix")
    path = unique_id[len(zeit.cms.interfaces.ID_NAMESPACE):]
    cms_config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.cms')
    prefix = cms_config[prefix]
    if not prefix.endswith('/'):
        prefix = prefix + '/'
    return urllib.parse.urljoin(prefix, path)


# it would be nicer if this were a named adapter, but then we wouldn't have
# access to the name, so that's not feasible
@zope.component.adapter(zeit.cms.interfaces.ICMSContent, str)
@zope.interface.implementer(zeit.cms.browser.interfaces.IPreviewURL)
def preview_url(content, preview_type):
    try:
        return prefixed_url(preview_type + '-prefix', content.uniqueId)
    except ValueError:
        pass


class PreviewBase(zeit.cms.browser.view.Base):
    """Base class for preview."""

    preview_type = None  # override in subclass

    def __call__(self):
        preview_object = zeit.cms.browser.interfaces.IPreviewObject(
            self.context, self.context)
        preview_url = zope.component.getMultiAdapter(
            (preview_object, self.preview_type),
            zeit.cms.browser.interfaces.IPreviewURL)
        query_string = self.request.environment['QUERY_STRING']
        if query_string:
            preview_url += '?%s' % query_string
        return self.redirect(preview_url, trusted=True)


class Preview(PreviewBase):

    preview_type = 'preview'


class Live(PreviewBase):

    preview_type = 'live'
