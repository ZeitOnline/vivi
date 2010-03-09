# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pybrightcove.connection
import zope.app.appsetup.product


def connection_factory():
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.brightcove')
    return pybrightcove.connection.APIConnection(
        config['read-token'],
        config['write-token'],
        config['read-url'],
        config['write-url'])
