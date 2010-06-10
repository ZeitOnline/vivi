# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import BTrees.Length
import csv
import grokcore.component
import persistent
import random
import zc.queue
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.workflow.interfaces
import zeit.vgwort.interfaces
import zope.component
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
            self.add(public_token, private_token)

    def add(self, public_token, private_token):
        self._data.put((public_token, private_token))
        self._len.change(1)

    def claim(self):
        if len(self) == 0:
            raise ValueError("No tokens available.")
        value = self._data.pull(random.randint(0, len(self) - 1))
        self._len.change(-1)
        return value

    def order(self, amount):
        service = zope.component.getUtility(
            zeit.vgwort.interfaces.IPixelService)
        return service.order_pixels(amount)

    def __len__(self):
        return self._len()


class Token(zeit.cms.content.dav.DAVPropertiesAdapter):

    grokcore.component.provides(zeit.vgwort.interfaces.IToken)

    zeit.cms.content.dav.mapProperties(
        zeit.vgwort.interfaces.IToken,
        'http://namespaces.zeit.de/CMS/vgwort',
        ('public_token', 'private_token'),
        live=True)


@grokcore.component.subscribe(
    zeit.vgwort.interfaces.IGenerallyReportableContent,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def add_token(context, event):
    if context != event.master:
        # Only assign tokens to the master
        return
    token = zeit.vgwort.interfaces.IToken(context)
    if token.public_token:
        # Already has a token. Do nothing then.
        return
    tokens = zope.component.getUtility(zeit.vgwort.interfaces.ITokens)
    token.public_token, token.private_token = tokens.claim()


@grokcore.component.subscribe(
    zeit.cms.content.interfaces.ISynchronisingDAVPropertyToXMLEvent)
def ignore_private_token(event):
    if (event.namespace == 'http://namespaces.zeit.de/CMS/vgwort' and
        event.name == 'private_token'):
        event.veto()
