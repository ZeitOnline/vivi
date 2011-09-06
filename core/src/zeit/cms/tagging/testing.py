# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import UserDict


class InMemoryTagger(UserDict.DictMixin):

    # XXX This is used as an adapter in at least one place, and instantiated
    # without context elsewhere. Should be done more cleanly at some point.
    def __init__(self, context=None):
        self.data = {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def keys(self):
        return [tag.code for tag in self.values()]

    def values(self):
        return sorted(self.data.values(), key=lambda x: x.weight, reverse=True)
