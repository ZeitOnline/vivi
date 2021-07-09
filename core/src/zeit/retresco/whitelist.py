import grokcore.component as grok
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.tag
import zeit.retresco.interfaces
import zope.component


@grok.implementer(zeit.cms.tagging.interfaces.IWhitelist)
class Whitelist(grok.GlobalUtility):
    """Search for known keywords using the Retresco API."""

    def search(self, term):
        return self._tms.get_keywords(term)

    def locations(self, term):
        return self._tms.get_locations(term)

    def get(self, id):
        return zeit.cms.tagging.tag.Tag.from_code(id)

    @property
    def _tms(self):
        return zope.component.getUtility(zeit.retresco.interfaces.ITMS)


@grok.implementer(zeit.cms.tagging.interfaces.ITopicpages)
class Topicpages(grok.GlobalUtility):

    def get_topics(self, start=0, rows=25):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        return tms.get_topicpages(start, rows)
