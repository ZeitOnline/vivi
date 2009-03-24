# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.interfaces
import zeit.cms.content.metadata
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zope.interface


CENTERPAGE_TEMPLATE = """\
<centerpage xmlns:py="http://codespeak.net/lxml/objectify/pytype">
    <head/>
    <body/>
</centerpage>"""

class CenterPage(zeit.cms.content.metadata.CommonMetadata):
    """XXX docme"""

    zope.interface.implements(zeit.content.cp.interfaces.ICenterPage)

    default_template = CENTERPAGE_TEMPLATE


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'centerpage')
resourceFactory = zope.component.adapter(
    zeit.content.cp.interfaces.ICenterPage)(resourceFactory)
