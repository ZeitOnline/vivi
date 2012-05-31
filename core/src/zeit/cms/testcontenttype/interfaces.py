# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt


import zeit.cms.content.interfaces


class ITestContentType(
    zeit.cms.content.interfaces.ICommonMetadata,
    zeit.cms.content.interfaces.IXMLContent):
    """A type for testing."""


ITestContentType.setTaggedValue('zeit.cms.type', 'testcontenttype')
ITestContentType.setTaggedValue(
    'zeit.cms.addform', 'zeit.cms.testcontenttype.Add')
