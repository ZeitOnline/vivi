import BTrees
import grokcore.component as grok
import persistent
import zc.relation.catalog
import zope.interface

import zeit.cms.interfaces
import zeit.cms.relation.interfaces


@zope.interface.implementer(zeit.cms.relation.interfaces.IRelations)
class Relations(persistent.Persistent):
    """Handles relations between content."""

    def __init__(self):
        super().__init__()
        self._catalog = zc.relation.catalog.Catalog(
            _dump_content, _load_content, btree=BTrees.family32.OI
        )

    # IRelations

    def index(self, obj):
        self._catalog.index(obj)

    def get_relations(self, obj):
        index = 'referenced_by'
        token = list(self._catalog.tokenizeValues([obj], index))[0]
        if token is None:
            return ()
        # TODO: add some code to remove removed objects from the index
        return (obj for obj in self._catalog.findRelations({index: token}) if obj is not None)

    def add_index(self, element, multiple=False):
        """add a value index for given element."""
        self._catalog.addValueIndex(
            element, _dump_content, _load_content, btree=BTrees.family32.OI, multiple=multiple
        )


def _dump_content(content, catalog, cache):
    return content.uniqueId


def _load_content(token, catalog, cache):
    return zeit.cms.interfaces.ICMSContent(token, None)


def referenced_by(content, catalog):
    """Index for the zeit.cms.relation catalog."""
    return zeit.cms.relation.interfaces.IReferences(content, None)


@grok.adapter(zeit.cms.interfaces.ICMSContent)
@grok.implementer(zeit.cms.relation.interfaces.IReferences)
def references(context):
    result = []
    for name, adapter in zope.component.getAdapters(
        (context,), zeit.cms.relation.interfaces.IReferenceProvider
    ):
        if not name:
            raise ValueError(
                'IReferenceProvider %r is registered without a name,'
                ' this will cause configuration conflicts.'
            )
        result.extend(adapter)
    return result
