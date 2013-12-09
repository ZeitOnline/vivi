# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.browser.preview
import zeit.magazin.interfaces


@grok.adapter(zeit.magazin.interfaces.IZMOContent, basestring)
@grok.implementer(zeit.cms.browser.interfaces.IPreviewURL)
def preview_url(content, preview_type):
    return zeit.cms.browser.preview.prefixed_url(
        'zmo-%s-prefix' % preview_type, content.uniqueId)


# XXX there also is a (basestring, basestring) variant of the adapter
# which is used by zeit.find to caluclate preview-urls for search results
# without looking up the content object first. What do we do about that?
