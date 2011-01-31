# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.tagging.interfaces


class Tags(object):
    """Property which stores tag data in DAV."""

    def __get__(self, instance, class_):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance, None)
        if tagger is None:
            return frozenset()
        return frozenset(tag for tag in tagger.values() if not tag.disabled)

    def __set__(self, instance, value):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance)
        for tag in list(tagger.values()):  # list to avoid dictionary changed
                                           #  during iteration
            tag.disabled = (tag not in value)
