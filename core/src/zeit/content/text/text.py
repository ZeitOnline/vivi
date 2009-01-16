# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import StringIO

import persistent
import zope.app.container.contained

import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.content.text.interfaces


class Text(persistent.Persistent,
           zope.app.container.contained.Contained):

    zope.interface.implements(zeit.content.text.interfaces.IText,
                              zeit.cms.interfaces.IAsset)

    uniqueId = None

    text = None
    encoding = zeit.cms.content.dav.DAVProperty(
        zeit.content.text.interfaces.IText['encoding'],
        zeit.content.text.interfaces.DAV_NAMESPACE, 'encoding',
        use_default=True)


@zope.interface.implementer(zeit.cms.interfaces.ICMSContent)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def text_factory(context):
    data = context.data.read()
    text = Text()
    encoding = text.encoding  # Read from the DAV properties
    unicode_data = None
    if encoding:
        try:
            unicode_data = unicode(data, encoding)
        except UnicodeDecodeError:
            pass

    if unicode_data is None:
        # Guess encoding
        for encoding_term in (
            zeit.content.text.interfaces.IText['encoding'].vocabulary):
            encoding = encoding_term.value
            try:
                unicode_data = unicode(data, encoding)
            except UnicodeDecodeError:
                pass
            else:
                break

    assert unicode_data is not None

    if encoding != text.encoding:
        text.encoding = encoding
    text.text = unicode_data
    return text


@zope.component.adapter(zeit.content.text.interfaces.IText)
@zope.interface.implementer(zeit.connector.interfaces.IResource)
def resource_factory(context):
    return zeit.cms.connector.Resource(
        context.uniqueId, context.__name__, 'text',
        StringIO.StringIO(context.text.encode(context.encoding)),
        contentType='text/plain',  # XXX
        properties=zeit.cms.interfaces.IWebDAVProperties(context))
