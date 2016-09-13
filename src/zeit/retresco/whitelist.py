import zeit.cms.tagging.interfaces
import zeit.retresco.interfaces
import zeit.retresco.tag
import zope.component
import zope.interface


class Whitelist(object):
    """Search for known keywords using the Retresco API."""

    zope.interface.implements(zeit.cms.tagging.interfaces.IWhitelist)

    def search(self, term):
        tms = zope.component.getUtility(zeit.retresco.interfaces.ITMS)
        return tms.get_keywords(term)

    def get(self, id):
        return zeit.retresco.tag.Tag.from_code(id)
