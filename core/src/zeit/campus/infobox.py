import grokcore.component as grok
import zeit.cms.content.dav
import zeit.cms.interfaces
import zeit.campus.interfaces


class Debate(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.implements(zeit.campus.interfaces.IDebate)

    action_url = zeit.cms.content.dav.DAVProperty(
        zeit.campus.interfaces.IDebate['action_url'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'debate_action_url')
