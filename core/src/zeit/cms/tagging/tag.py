# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import copy
import grokcore.component as grok
import zeit.cms.browser.interfaces
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zope.component
import zope.interface
import zope.location.interfaces
import zope.publisher.interfaces
import zope.site.hooks
import zope.site.interfaces
import zope.traversing.browser
import zope.traversing.browser.absoluteurl
import zope.traversing.interfaces


class Tags(object):
    """Property which stores tag data in DAV."""

    def __get__(self, instance, class_):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance, None)
        if tagger is None:
            return ()
        return tuple(tagger.values())

    def __set__(self, instance, value):
        # this is a little convoluted since we want to leave tags that have
        # already been set alone as much as possible (since they might have
        # more metadata in their XML representation than the ones from the
        # whitelist)
        tagger = zeit.cms.tagging.interfaces.ITagger(instance)
        for tag in value:
            if tag.code not in tagger:
                tagger[tag.code] = tag
        codes = [x.code for x in value]
        for code in list(tagger):
            if code not in codes:
                del tagger[code]
        tagger.updateOrder((x.code for x in value))
        tagger.set_pinned([x.code for x in value if x.pinned])


class Tag(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ITag,
                              zeit.cms.interfaces.ICMSContent)

    def __init__(self, code, label, pinned=False, entity_type=None):
        self.code = code
        self.label = label
        self.pinned = pinned
        self.entity_type = entity_type

    def __eq__(self, other):
        # XXX this is not a generic equality check. From a domain perspective,
        # two tags are the same when their codes are the same. However, since
        # we want to edit ``pinned``, and formlib compares the *list* of
        # keywords, which uses == on the items, we need to include pinned here.
        if other is None:
            return False
        return self.code == other.code and self.pinned == other.pinned

    @property
    def uniqueId(self):
        return zeit.cms.tagging.interfaces.ID_NAMESPACE + self.code


@grok.adapter(
    basestring, name=zeit.cms.tagging.interfaces.ID_NAMESPACE)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_tag(unique_id):
    assert unique_id.startswith(
        zeit.cms.tagging.interfaces.ID_NAMESPACE)
    token = unique_id.replace(
        zeit.cms.tagging.interfaces.ID_NAMESPACE, '', 1)
    whitelist = zope.component.getUtility(
        zeit.cms.tagging.interfaces.IWhitelist)
    # return a copy so clients can manipulate the Tag object (e.g. set
    # ``pinned`` on it). This is analogue to the way zeit.intrafind.Tagger
    # works, it also returns fresh Tag objects on each read access.
    return copy.copy(whitelist.get(token))


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    zope.component.adapts(Tag, zeit.cms.browser.interfaces.ICMSLayer)

    def __str__(self):
        base = zope.traversing.browser.absoluteURL(
            zope.site.hooks.getSite(), self.request)
        return base + '/++tag++' + self.context.code


class TagTraverser(grok.MultiAdapter):

    zope.interface.implements(zope.traversing.interfaces.ITraversable)
    grok.adapts(
        zope.site.interfaces.IRootFolder,
        zope.publisher.interfaces.IRequest)
    grok.name('tag')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        tag = whitelist.get(name)
        if tag is None:
            raise zope.location.interfaces.LocationError(self.context, name)
        return tag
