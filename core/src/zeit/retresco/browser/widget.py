import urlparse
import zeit.cms.tagging.browser.widget
import zeit.retresco.interfaces
import zope.component


class RetrescoTagWidget(zeit.cms.tagging.browser.widget.Widget):
    """Edit widget for tags from Retresco.

    After intrafind got removed, the baseclass can be used as only widget
    again.

    """

    @property
    def tms_host(self):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        return urlparse.urlparse(tms.url).netloc
