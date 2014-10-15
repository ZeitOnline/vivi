import zeit.cms.redirect.interfaces
import zope.interface


class FakeLookup(object):

    zope.interface.implements(zeit.cms.redirect.interfaces.ILookup)

    def __init__(self):
        self.redirects = {}

    def rename(self, old_id, new_id):
        for source, target in self.redirects.items():
            if target == old_id:
                self.redirects[source] = new_id
        self.redirects[old_id] = new_id

    def find(self, uniqueId):
        return self.redirects.get(uniqueId)
