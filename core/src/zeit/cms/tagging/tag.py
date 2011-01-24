# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.tagging.interfaces


class Tags(object):

    def __get__(self, instance, class_):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance)
        return frozenset(tag for tag in tagger.values() if tag.active)

    def __set__(self, instance, value):
        tagger = zeit.cms.tagging.interfaces.ITagger(instance)
        for tag in tagger.values():
            tag.active = (tag in value)
