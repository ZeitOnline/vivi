import grokcore.component as grok
import zeit.cms.tagging.interfaces
import zeit.retresco.interfaces
import zeit.retresco.tag
import zope.component
import zope.interface


class Whitelist(grok.GlobalUtility):
    """Search for known keywords using the Retresco API."""

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def search(self, term):
        return self._tms.get_keywords(term)

    def locations(self, term):
        return self._tms.get_locations(term)

    def get(self, id):
        return zeit.retresco.tag.Tag.from_code(id)

    @property
    def _tms(self):
        return zope.component.getUtility(zeit.retresco.interfaces.ITMS)
