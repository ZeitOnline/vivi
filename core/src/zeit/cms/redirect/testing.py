import zeit.cms.redirect.interfaces
import zope.interface


@zope.interface.implementer(zeit.cms.redirect.interfaces.ILookup)
class FakeLookup:
    def __init__(self):
        self.redirects = {}

    def rename(self, old_id, new_id):
        for source, target in self.redirects.items():
            if target == old_id:
                self.redirects[source] = new_id
        self.redirects[old_id] = new_id

    def find(self, uniqueId):
        return self.redirects.get(uniqueId)
