# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

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
        tagger = zeit.cms.tagging.interfaces.ITagger(instance)
        for tag in list(tagger.values()):
            if tag not in value:
                del tagger[tag.code]
        tagger.updateOrder((x.code for x in value))


class Tag(object):

    zope.interface.implements(zeit.cms.tagging.interfaces.ITag,
                              zeit.cms.interfaces.ICMSContent)

    def __init__(self, code, label):
        self.code = code
        self.label = label

    def __eq__(self, other):
        if other is None:
            return False
        return self.code == other.code

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
    return whitelist.get(token)


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
