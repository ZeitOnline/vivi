import BTrees
import persistent
import sys
import zeit.brightcove.interfaces
import zeit.cms.generation
import zope.component
import zope.container.contained


@zope.interface.implementer(zeit.brightcove.interfaces.IRepository)
class Repository(persistent.Persistent, zope.container.contained.Contained):
    # Stub so the generation can remove the objects properly

    def __init__(self):
        self._data = BTrees.family32.OO.BTree()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, obj):
        self._data[key] = obj

    def get(self, key):
        return self._data.get(key)

    def __iter__(self):
        return iter(self._data)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


class Content(persistent.Persistent, zope.container.contained.Contained):
    # Stub so the generation can remove the objects properly
    pass


Video = Playlist = Content


def update(root):
    # Fake the old locations of persistent objects
    from zeit.brightcove.generation import evolve2

    sys.modules['zeit.brightcove.repository'] = evolve2
    sys.modules['zeit.brightcove.content'] = evolve2
    # Remove the brightcove repository from ZODB.
    try:
        repository = zope.component.queryUtility(zeit.brightcove.interfaces.IRepository)
        if repository is not None:
            site_manager = zope.component.getSiteManager()
            site_manager.unregisterUtility(repository, zeit.brightcove.interfaces.IRepository)
            del root['repository-brightcove']
    finally:
        del sys.modules['zeit.brightcove.repository']
        del sys.modules['zeit.brightcove.content']


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
