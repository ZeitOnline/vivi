# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import grokcore.component
import zeit.brightcove.video
import zeit.brightcove.interfaces
import zope.container.btree


class Repository(zope.container.btree.BTreeContainer):

    _type_class_map = {
        'video': zeit.brightcove.video.Video
    }

    def __getitem__(self, key):
        class_, id = self._parse_key(key)
        if class_ is None:
            raise KeyError(key)
        for obj in class_.find_by_ids([id]):
            # The brightcove API is rahter stupid and returns [None] instead of
            # [] when there is no result. *ARGH*
            if obj.data is not None:
                return obj
        raise KeyError(key)

    def _parse_key(self, key):
        if ':' in key:
            type_, id_ = key.split(':', 1)
            return self._type_class_map.get(type_), id_
        return None, None
