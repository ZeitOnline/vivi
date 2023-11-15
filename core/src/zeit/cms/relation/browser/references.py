import zeit.cms.relation.interfaces
import zope.component


class Index:
    @property
    def references(self):
        rel = zope.component.getUtility(zeit.cms.relation.interfaces.IRelations)
        return sorted(rel.get_relations(self.context), key=lambda x: x.uniqueId)
