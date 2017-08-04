import grokcore.component as grok
import zeit.arbeit.interfaces
import zeit.cms.content.dav
import zeit.cms.interfaces


class Debate(zeit.cms.content.dav.DAVPropertiesAdapter):

    grok.implements(zeit.arbeit.interfaces.IDebate)

    action_url = zeit.cms.content.dav.DAVProperty(
        zeit.arbeit.interfaces.IDebate['action_url'],
        zeit.cms.interfaces.DOCUMENT_SCHEMA_NS,
        'debate_action_url')
