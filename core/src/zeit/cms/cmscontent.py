import grokcore.component as grok
import six
import six.moves.urllib.parse
import zeit.cms.interfaces
import zeit.cms.workingcopy.interfaces
import zope.component


@grok.adapter(six.string_types[0])
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_cms_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    name = '%s://' % (parsed.scheme or '<no-scheme>')
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)


@grok.adapter(six.string_types[0], name='http://')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def http_scheme_unique_id_to_cms_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    assert parsed.scheme == 'http'
    name = 'http://%s/' % parsed.netloc
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)


# Sigh, more copy&paste
@grok.adapter(six.string_types[0], name='https://')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def https_scheme_unique_id_to_cms_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    assert parsed.scheme == 'https'
    name = 'https://%s/' % parsed.netloc
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)


@grok.adapter(six.string_types[0], name='<no-scheme>://')
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def no_scheme_unique_id_to_cms_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    name = '<no-scheme>://%s/' % (parsed.netloc or '<no-netloc>')
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSContent, name=name)


# XXX Having to duplicate all these is kludgy.

@grok.adapter(six.string_types[0])
@grok.implementer(zeit.cms.interfaces.ICMSWCContent)
def unique_id_to_cmswc_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    name = '%s://' % (parsed.scheme or '<no-scheme>')
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSWCContent, name=name)


@grok.adapter(six.string_types[0], name='http://')
@grok.implementer(zeit.cms.interfaces.ICMSWCContent)
def http_scheme_unique_id_to_cmswc_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    assert parsed.scheme == 'http'
    name = 'http://%s/' % parsed.netloc
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSWCContent, name=name)


@grok.adapter(six.string_types[0], name='https://')
@grok.implementer(zeit.cms.interfaces.ICMSWCContent)
def https_scheme_unique_id_to_cmswc_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    assert parsed.scheme == 'https'
    name = 'https://%s/' % parsed.netloc
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSWCContent, name=name)


@grok.adapter(six.string_types[0], name='<no-scheme>://')
@grok.implementer(zeit.cms.interfaces.ICMSWCContent)
def no_scheme_unique_id_to_cmswc_content(unique_id):
    parsed = six.moves.urllib.parse.urlparse(unique_id)
    name = '<no-scheme>://%s/' % (parsed.netloc or '<no-netloc>')
    return zope.component.queryAdapter(
        unique_id, zeit.cms.interfaces.ICMSWCContent, name=name)


def resolve_wc_or_repository(unique_id):
    obj = zeit.cms.interfaces.ICMSWCContent(unique_id, None)
    if obj is None:
        obj = zeit.cms.interfaces.ICMSContent(unique_id, None)
    return obj
