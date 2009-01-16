# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees
import persistent
import zc.relation.catalog
import zc.relation.interfaces
import zeit.cms.relation.interfaces
import zope.interface


class Relations(persistent.Persistent):
    """Handles relations between content."""

    zope.interface.implements(zeit.cms.relation.interfaces.IRelations)

    def __init__(self):
        super(Relations, self).__init__()
        self._catalog = zc.relation.catalog.Catalog(
            _dump_content, _load_content, btree=BTrees.family32.OI)

    # IRelations

    def index(self, obj):
        self._catalog.index(obj)

    def get_relations(self, obj, name):
        token = list(self._catalog.tokenizeValues([obj], name))[0]
        if token is None:
            return ()
        # TODO: add some code to remove removed objects from the index
        return (obj for obj in self._catalog.findRelations({name: token})
                if obj is not None)

    def add_index(self, element, multiple=False):
        """add a value index for given element."""
        self._catalog.addValueIndex(
            element, _dump_content, _load_content,
            btree=BTrees.family32.OI, multiple=multiple)


def _dump_content(content, catalog, cache):
    return content.uniqueId


def _load_content(token, catalog, cache):
    repository = cache.get('repository')
    if repository is None:
        cache['repository'] = repository = zope.component.getUtility(
            zeit.cms.repository.interfaces.IRepository)
    try:
        return repository.getContent(token)
    except KeyError:
        # If the object doesn't exist, return None
        return None
