# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pybrightcove.video
import grokcore.component
import zeit.brightcove.interfaces
import zope.container.btree


class Repository(zope.container.btree.BTreeContainer):

    _type_class_map = {
        'video': pybrightcove.video.Video,
    }

    def __getitem__(self, key):
        class_, id = self._parse_key(key)
        if class_ is None:
            raise KeyError(key)
        results = class_.find_by_ids([id], self.connection)
        iter(results).next()


    def _parse_key(self, key):
        if ':' in key:
            type_, id_ = key.split(':', 1)
            return self._type_class_map.get(type_), id_
        return None, None

    @property
    def connection(self):
        return zope.component.getUtility(
            zeit.brightcove.interfaces.IAPIConnection)
