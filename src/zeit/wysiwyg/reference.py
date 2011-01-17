# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.traversing.interfaces import IContainmentRoot
import lovely.remotetask.processor
import urllib
import zeit.cms.checkout.interfaces
import zeit.cms.interfaces
import zeit.cms.relation.interfaces
import zeit.wysiwyg.interfaces
import zope.component
import zope.interface
import zope.location.interfaces
import zope.traversing.browser.absoluteurl
import zope.traversing.browser.interfaces


@zope.component.adapter(zeit.cms.interfaces.ICMSContent)
@zope.interface.implementer(zeit.cms.relation.interfaces.IReferenceProvider)
def html_references(context):
    html_content = zeit.wysiwyg.interfaces.IHTMLContent(context, None)
    if html_content is None:
        return
    return html_content.references


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_metadata_on_checkin(context, event):
    __traceback_info__ = (context.uniqueId,)
    html_content = zeit.wysiwyg.interfaces.IHTMLContent(context, None)
    if html_content is None:
        return
    html_content.html = html_content.html


class AbsoluteURL(zope.publisher.browser.BrowserView):
    # update_metadata_on_checkin works by converting to HTML and back again.
    # It may be called from inside a RemoteTask (when triggered by
    # zeit.cms.relation), where the default AbsoluteURL doesn't work, so we
    # need to provide one.
    #
    # We don't need to (and do not) provide a sensible URL, so the HTML
    # produced inside the RemoteTask is bogus. But we're not interested in the
    # HTML itself, the only important thing is that it converts back to XML
    # properly.

    zope.component.adapts(
        zope.interface.Interface,
        lovely.remotetask.processor.ProcessorRequest)
    zope.interface.implements(zope.traversing.browser.interfaces.IAbsoluteURL)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        if (context is None or IContainmentRoot.providedBy(context)):
            # IMPORTANT: this is bogus (see above for an explanation)
            return 'http://HOST/'

        context = zope.location.interfaces.ILocation(context)
        container = getattr(context, '__parent__', None)
        if container is None:
            raise TypeError(
                zope.traversing.browser.absoluteurl._insufficientContext)

        url = str(zope.component.getMultiAdapter(
            (container, self.request),
            zope.traversing.browser.interfaces.IAbsoluteURL))
        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError(
                zope.traversing.browser.absoluteurl._insufficientContext)

        if name:
            url += '/' + urllib.quote(
                name.encode('utf-8'),
                zope.traversing.browser.absoluteurl._safe)

        return url

    def __call__(self):
        return self.__str__()
