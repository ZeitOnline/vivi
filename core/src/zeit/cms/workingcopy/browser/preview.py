import urllib2
import urlparse
import zeit.cms.browser.preview
import zeit.cms.interfaces
import zeit.connector.interfaces
import zope.component


class WorkingcopyPreview(zeit.cms.browser.preview.Preview):
    """Preview for workingcopy versions of content objects.

    This supports two modes of operation:

    1. Upload the workingcopy version of an object to the repository, retrieve
    the html and return it (proxying the result).
    2. Give the workingcopy URL to the preview service (for those who can
    traverse it directly) and redirect to it as for the repository preview.

    """

    def __call__(self):
        url = self.get_preview_url_for(self.context)
        if self.should_upload(url):
            return self.proxied_preview()
        else:
            return self.redirect(self.workingcopy_url(url), trusted=True)

    def should_upload(self, url):
        return 'friedbert' not in url  # XXX Really kludgy heuristics

    def proxied_preview(self):
        preview_obj = self.temporary_checkin()
        url = self.get_preview_url_for(preview_obj)
        preview_request = urllib2.urlopen(url)
        del preview_obj.__parent__[preview_obj.__name__]
        return preview_request.read()

    def get_preview_url_for(self, preview_context):
        url = zope.component.getMultiAdapter(
            (preview_context, self.preview_type),
            zeit.cms.browser.interfaces.IPreviewURL)
        querystring = self.request.environment['QUERY_STRING']
        if querystring:
            url = '%s?%s' % (url, querystring)
        return url

    def temporary_checkin(self):
        content = zeit.cms.interfaces.ICMSContent(
            zeit.connector.interfaces.IResource(self.context))
        content.uniqueId = None

        target_folder = zeit.cms.interfaces.ICMSContent(
            self.context.uniqueId).__parent__

        temp_id = self.get_temp_id(self.context.__name__)
        target_folder[temp_id] = content

        return content

    def get_temp_id(self, name):
        return 'preview-%s-%s' % (
            self.request.principal.id, name)

    def workingcopy_url(self, url):
        repository_path = urlparse.urlparse(self.context.uniqueId).path
        fullpath = self.url(self.context)
        workingcopy = self.url(zope.component.getUtility(
            zeit.cms.workingcopy.interfaces.IWorkingcopyLocation))
        workingcopy_path = fullpath.replace(workingcopy, '')
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        workingcopy_path = config[
            'friebert-wc-preview-prefix'] + workingcopy_path
        url = url.replace(repository_path, workingcopy_path)
        return url
