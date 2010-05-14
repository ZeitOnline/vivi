# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

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

    def load(self, csv_file):
        reader = csv.reader(csv_file, delimiter=';')
        reader.next()  # skip first line
        for public_token, private_token in reader:
            self._data.put((public_token, private_token))

    def claim(self):
        if len(self) == 0:
            raise ValueError("No tokens available.")
        return self._data.pull(random.randint(0, len(self) - 1))

    def __len__(self):
        return len(self._data)
