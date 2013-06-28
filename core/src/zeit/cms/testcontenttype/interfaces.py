# Copyright (c) 2007-2013 gocept gmbh & co. kg
# See also LICENSE.txt


import zeit.cms.content.interfaces
import zeit.cms.tagging.interfaces


class ITestContentType(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.IXMLContent):
    """A type for testing."""

    keywords = zeit.cms.tagging.interfaces.Keywords(
        required=False,
        default=())


ITestContentType.setTaggedValue('zeit.cms.type', 'testcontenttype')
ITestContentType.setTaggedValue(
    'zeit.cms.addform', 'zeit.cms.testcontenttype.Add')
