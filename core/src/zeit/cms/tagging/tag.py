# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zope.component
import zope.interface
import zope.schema
import zope.traversing.browser
import zope.traversing.browser.absoluteurl


class Tag(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ITag,
                              zeit.cms.interfaces.ICMSContent)

    def __init__(self, label):
        self.label = self.code = label

    def __eq__(self, other):
        if other is None:
            return False
        return self.label == other.label

    @property
    def uniqueId(self):
        return zeit.cms.tagging.interfaces.ID_NAMESPACE + self.code


@grok.adapter(
    basestring, name=zeit.cms.tagging.interfaces.ID_NAMESPACE)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_toteasergroup(unique_id):
    assert unique_id.startswith(
        zeit.cms.tagging.interfaces.ID_NAMESPACE)
    token = unique_id.replace(
        zeit.cms.tagging.interfaces.ID_NAMESPACE, '', 1)
    whitelist = zope.component.getUtility(
        zeit.cms.tagging.interfaces.IWhitelist)
    return whitelist.get(token)


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    zope.component.adapts(Tag, zeit.cms.browser.interfaces.ICMSLayer)

    def __str__(self):
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        base = zope.traversing.browser.absoluteURL(whitelist, self.request)
        return base + '/' + self.context.code


class TagsProperty(object):

    def __init__(self, target_name):
        self.target_name = target_name

    def __get__(self, instance, cls):
        return tuple(Tag(uid) for uid in getattr(instance, self.target_name))

    def __set__(self, instance, tags):
        setattr(instance, self.target_name, tuple(tag.code for tag in tags))


class KeywordTagsProperty(TagsProperty):

    def __init__(self, target_name, other_name):
        self.target_name = target_name
        self.other_name = other_name

    def __set__(self, instance, tags):
        field = zeit.cms.tagging.interfaces.ITaggable['keywords']
        values = set(field.bind(instance).value_type.source)
        codes = tuple(tag.code for tag in tags)
        setattr(instance, self.target_name, codes)
        setattr(instance, self.other_name,
                tuple(set(tag.code for tag in values) - set(codes)))


TAGGING_NS = u"http://namespaces.zeit.de/CMS/tagging"


class Taggable(object):

    zope.interface.Interface(zeit.cms.tagging.interfaces.ITaggable)

    _keywords = zeit.cms.content.dav.DAVProperty(
        zope.schema.Tuple(value_type=zope.schema.TextLine(), default=()),
        TAGGING_NS, 'keywords', use_default=True)

    keywords = KeywordTagsProperty('_keywords', '_disabled_keywords')

    _disabled_keywords = zeit.cms.content.dav.DAVProperty(
        zope.schema.Tuple(value_type=zope.schema.TextLine(), default=()),
        TAGGING_NS, 'disabled_keywords', use_default=True)

    disabled_keywords = TagsProperty('_disabled_keywords')
