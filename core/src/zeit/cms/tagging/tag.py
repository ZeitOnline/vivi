import collections
import copy

import grokcore.component as grok
import zope.cachedescriptors.property
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.security.proxy

import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces


class Tags:
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
        value = self._remove_duplicates(value)
        for tag in value:
            if tag.code not in tagger:
                tagger[tag.code] = tag
        codes = [x.code for x in value]
        for code in list(tagger):
            if code not in codes:
                del tagger[code]
        tagger.updateOrder((x.code for x in value))
        tagger.set_pinned([x.code for x in value if x.pinned])

    def _remove_duplicates(self, tags):
        result = collections.OrderedDict()
        for tag in tags:
            if tag.code not in result:
                result[tag.code] = tag
        return result.values()


@zope.interface.implementer(zeit.cms.tagging.interfaces.ITag)
class Tag:
    """Representation of a keyword."""

    # This is stored in DAV properties, changing it requires a mass-migration.
    SEPARATOR = '☃'

    def __init__(self, label, entity_type, link=None):
        self.label = label or ''
        self.entity_type = entity_type
        self.pinned = False  # pinned state is set from outside after init
        self.__name__ = self.code  # needed to fulfill `ICMSContent`
        self.link = link
        # For zeit.web, link is populated by ITMS.get_article_topiclinks() with
        # the TMS-provided path to the corresponding topicpage; without a
        # leading slash, so it plays nice with route_url() which already has
        # the slash.

    @zope.cachedescriptors.property.Lazy
    def code(self):
        # `code` is only used for internal purposes. It is used as key in
        # `Tagger` and `Tags`, in DAV-Properties to mark a `Tag` pinned and as
        # `part of the `AbsoluteURL` and `Traverser` functionality.
        return ''.join((self.entity_type, self.SEPARATOR, self.label))

    @classmethod
    def from_code(cls, code):
        if cls.SEPARATOR not in code:
            return None
        entity_type, sep, label = code.partition(cls.SEPARATOR)
        return cls(label, entity_type)

    def __eq__(self, other):
        # XXX this is not a generic equality check. From a domain perspective,
        # two tags are the same when their codes are the same. However, since
        # we want to edit ``pinned``, and formlib compares the *list* of
        # keywords, which uses == on the items, we need to include pinned here.
        if not zeit.cms.tagging.interfaces.ITag.providedBy(other):
            return False
        return self.code == other.code and self.pinned == other.pinned

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def uniqueId(self):
        return '{}{}'.format(
            zeit.cms.tagging.interfaces.ID_NAMESPACE,
            self.code.encode('unicode_escape').decode('ascii'),
        )

    @property
    def title(self):
        return '%s (%s)' % (self.label, self.entity_type.title())

    def __repr__(self):
        return '<%s.%s %s>' % (self.__class__.__module__, self.__class__.__name__, self.uniqueId)


@grok.subscribe(zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def veto_tagging_properties(event):
    if event.namespace == 'http://namespaces.zeit.de/CMS/tagging':
        event.veto()


def add_ranked_tags_to_head(content):
    tagger = zeit.cms.tagging.interfaces.ITagger(content, None)
    if tagger:
        tags = zope.security.proxy.removeSecurityProxy(tagger).to_xml()
    else:
        tags = None

    xml = zope.security.proxy.removeSecurityProxy(content.xml)
    head = xml.find('head')
    if head is None:
        return

    existing = head.find('rankedTags')
    if tags is not None:
        if existing is not None:
            head.replace(existing, tags)
        else:
            head.append(tags)
    else:
        if existing is not None:
            head.remove(existing)


@grok.subscribe(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent,
)
def update_tags_on_checkin(content, event):
    # ICMSContent.providedBy(content) is True implicitly, since otherwise one
    # wouldn't be able to check it in.
    add_ranked_tags_to_head(content)


@grok.subscribe(zeit.cms.interfaces.ICMSContent, zope.lifecycleevent.ObjectModifiedEvent)
def update_tags_on_modify(content, event):
    if not zeit.cms.content.interfaces.IDAVPropertiesInXML.providedBy(content):
        return
    add_ranked_tags_to_head(content)


@grok.adapter(str, name=zeit.cms.tagging.interfaces.ID_NAMESPACE)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_tag(unique_id):
    assert unique_id.startswith(zeit.cms.tagging.interfaces.ID_NAMESPACE)
    token = unique_id.replace(zeit.cms.tagging.interfaces.ID_NAMESPACE, '', 1)
    # `zeit.retresco` generates unicode escaped uniqueIds, so we decode them.
    if isinstance(token, str):
        token = token.encode('utf-8')
    token = token.decode('unicode_escape')
    whitelist = zope.component.getUtility(zeit.cms.tagging.interfaces.IWhitelist)
    # return a copy so clients can manipulate the Tag object (e.g. set
    # ``pinned`` on it). This is analogue to the way zeit.intrafind.Tagger
    # works, it also returns fresh Tag objects on each read access.
    return copy.copy(whitelist.get(token))
