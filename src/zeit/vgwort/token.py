# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees.Length
import csv
import persistent
import random
import zc.queue
import zeit.vgwort.interfaces
import zope.container.contained
import zope.interface


class TokenStorage(persistent.Persistent,
                   zope.container.contained.Contained):

    zope.interface.implements(zeit.vgwort.interfaces.ITokens)

    def __init__(self):
        self._data = zc.queue.CompositeQueue(compositeSize=100)
        self._len = BTrees.Length.Length()

    def load(self, csv_file):
        reader = csv.reader(csv_file, delimiter=';')
        reader.next()  # skip first line
        for public_token, private_token in reader:
            self._data.put((public_token, private_token))
            self._len.change(1)

    def claim(self):
        if len(self) == 0:
            raise ValueError("No tokens available.")
        value = self._data.pull(random.randint(0, len(self) - 1))
        self._len.change(-1)
        return value

    def __len__(self):
        return self._len()
