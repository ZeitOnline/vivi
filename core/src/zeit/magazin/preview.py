import grokcore.component as grok
import zeit.cms.browser.preview
import zeit.magazin.interfaces


@grok.adapter(zeit.magazin.interfaces.IZMOContent, basestring)
@grok.implementer(zeit.cms.browser.interfaces.IPreviewURL)
def preview_url(content, preview_type):
    return zeit.cms.browser.preview.prefixed_url(
        'zmo-%s-prefix' % preview_type, content.uniqueId)
