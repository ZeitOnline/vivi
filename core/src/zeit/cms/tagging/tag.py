# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component as grok
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zope.interface


class Tags(object):
    """Property which stores tag data in DAV."""

    def __get__(self, instance, class_):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance, None)
        if tagger is None:
            return ()
        return tuple(tag for tag in tagger.values() if not tag.disabled)

    def __set__(self, instance, value):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance)
        for tag in list(tagger.values()):  # list to avoid dictionary changed
                                           # during iteration
            tag.disabled = (tag not in value)
            tag.weight = 0
        for weight, tag in enumerate(reversed(value), start=1):
            tag.weight = weight


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
