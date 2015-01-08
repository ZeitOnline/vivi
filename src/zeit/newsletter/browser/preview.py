import grokcore.component as grok
import zeit.cms.browser.preview
import zeit.newsletter.interfaces


@grok.adapter(zeit.newsletter.interfaces.INewsletter, basestring)
@grok.implementer(zeit.cms.browser.interfaces.IPreviewURL)
def preview_url(content, preview_type):
    return zeit.cms.browser.preview.prefixed_url(
        'newsletter-%s-prefix' % preview_type, content.uniqueId)
