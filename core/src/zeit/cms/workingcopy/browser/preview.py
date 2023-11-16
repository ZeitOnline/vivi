import urllib.parse
import urllib.request
import zeit.cms.browser.preview
import zeit.cms.interfaces
import zeit.connector.interfaces
import zope.component


class WorkingcopyPreview(zeit.cms.browser.preview.Preview):
    """Preview for workingcopy versions of content objects."""

    def __call__(self):
        url = self.get_preview_url_for(self.context)
        return self.redirect(self.workingcopy_url(url), trusted=True)

    def get_preview_url_for(self, preview_context):
        url = zope.component.getMultiAdapter(
            (preview_context, self.preview_type), zeit.cms.browser.interfaces.IPreviewURL
        )
        querystring = self.request.environment['QUERY_STRING']
        if querystring:
            url = '%s?%s' % (url, querystring)
        return url

    def workingcopy_url(self, url):
        repository_path = urllib.parse.urlparse(self.context.uniqueId).path
        fullpath = self.url(self.context)
        workingcopy = self.url(
            zope.component.getUtility(zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
        )
        workingcopy_path = fullpath.replace(workingcopy, '')
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        workingcopy_path = config['friebert-wc-preview-prefix'] + workingcopy_path
        url = url.replace(repository_path, workingcopy_path)
        return url
