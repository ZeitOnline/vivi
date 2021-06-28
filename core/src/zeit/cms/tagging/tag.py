import collections
import copy
import grokcore.component as grok
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.cms.tagging.interfaces
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.security.proxy


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


@grok.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def veto_tagging_properties(event):
    if event.namespace == 'http://namespaces.zeit.de/CMS/tagging':
        event.veto()


def add_ranked_tags_to_head(content):
    tagger = zeit.cms.tagging.interfaces.ITagger(content, None)
    xml = zope.security.proxy.removeSecurityProxy(content.xml)
    if tagger and xml.find('head') is not None:
        xml.head.rankedTags = zope.security.proxy.removeSecurityProxy(
            tagger).to_xml()
    else:
        try:
            del xml.head.rankedTags
        except AttributeError:
            pass


@grok.subscribe(
    zeit.cms.content.interfaces.IXMLRepresentation,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_tags_on_checkin(content, event):
    # ICMSContent.providedBy(content) is True implicitly, since otherwise one
    # wouldn't be able to check it in.
    add_ranked_tags_to_head(content)


@grok.subscribe(
    zeit.cms.interfaces.ICMSContent,
    zope.lifecycleevent.ObjectModifiedEvent)
def update_tags_on_modify(content, event):
    if not zeit.cms.content.interfaces.IXMLRepresentation.providedBy(content):
        return
    add_ranked_tags_to_head(content)


@grok.adapter(
    str, name=zeit.cms.tagging.interfaces.ID_NAMESPACE)
@grok.implementer(zeit.cms.interfaces.ICMSContent)
def unique_id_to_tag(unique_id):
    assert unique_id.startswith(
        zeit.cms.tagging.interfaces.ID_NAMESPACE)
    token = unique_id.replace(
        zeit.cms.tagging.interfaces.ID_NAMESPACE, '', 1)
    # `zeit.retresco` generates unicode escaped uniqueIds, so we decode them.
    if isinstance(token, str):
        token = token.encode('utf-8')
    token = token.decode('unicode_escape')
    whitelist = zope.component.getUtility(
        zeit.cms.tagging.interfaces.IWhitelist)
    # return a copy so clients can manipulate the Tag object (e.g. set
    # ``pinned`` on it). This is analogue to the way zeit.intrafind.Tagger
    # works, it also returns fresh Tag objects on each read access.
    return copy.copy(whitelist.get(token))
