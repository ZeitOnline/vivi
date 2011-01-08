# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Implementation of the test content type."""

import zope.component
import zope.interface

import zeit.cms.content.adapter
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.cms.testcontenttype.interfaces


class TestContentType(zeit.cms.content.metadata.CommonMetadata):
    """A type for testing."""

    zope.interface.implements(
        zeit.cms.testcontenttype.interfaces.ITestContentType,
        zeit.cms.interfaces.IEditorialContent)

    default_template = (
        '<testtype xmlns:py="http://codespeak.net/lxml/objectify/pytype">'
        '<head/><body/></testtype>')


test_content_type_factory = zeit.cms.content.adapter.xmlContentFactory(
    TestContentType)

resourceFactory = zeit.cms.content.adapter.xmlContentToResourceAdapterFactory(
    'testcontenttype')
resourceFactory = zope.component.adapter(
    zeit.cms.testcontenttype.interfaces.ITestContentType)(resourceFactory)
