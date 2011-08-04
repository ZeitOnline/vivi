# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Interface definitions for the test content type."""


import zope.interface


class ITestContentType(zope.interface.Interface):
    """A type for testing."""


ITestContentType.setTaggedValue('zeit.cms.type', 'testcontenttype')
