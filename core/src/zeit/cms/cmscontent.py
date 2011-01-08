# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import urlparse
import zeit.cms.interfaces
import zope.component


@grokcore.component.adapter(basestring)
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_cms_content(unique_id):
    parsed = urlparse.urlparse(unique_id)
    name = '%s://' % (parsed.scheme or '<no-scheme>')
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)


@grokcore.component.adapter(basestring, name='http://')
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def http_scheme_unique_id_to_cms_content(unique_id):
    parsed = urlparse.urlparse(unique_id)
    assert parsed.scheme == 'http'
    name = 'http://%s/' % parsed.netloc
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)


@grokcore.component.adapter(basestring, name='<no-scheme>://')
@grokcore.component.implementer(zeit.cms.interfaces.ICMSContent)
def no_scheme_unique_id_to_cms_content(unique_id):
    parsed = urlparse.urlparse(unique_id)
    name = '<no-scheme>://%s/' % (parsed.netloc or '<no-netloc>')
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)
