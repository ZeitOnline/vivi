# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$
"""Connector which integrates into Zope CA."""

import logging
import os
import threading

import zope.app.appsetup.product
import zope.component

import gocept.cache.property

import zeit.connector.connector
import zeit.connector.interfaces


logger = logging.getLogger(__name__)


class ZopeConnector(zeit.connector.connector.Connector):

    connections = gocept.cache.property.TransactionBoundCache(
        '_connections', threading.local)

    @property
    def body_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IResourceCache)

    @property
    def property_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IPropertyCache)

    @property
    def child_name_cache(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.IChildNameCache)

    @property
    def locktokens(self):
        return zope.component.getUtility(
            zeit.connector.interfaces.ILockInfoStorage)


def connectorFactory():
    """Factory for creating the connector with data from zope.conf."""
    config = zope.app.appsetup.product.getProductConfiguration(
        'zeit.connector')
    if config:
        root = config.get('document-store')
        if not root:
            raise ZConfig.ConfigurationError(
                "WebDAV server not configured properly.")
        search_root = config.get('document-store-search')
    else:
        root = os.environ.get('connector-url')
        search_root = os.environ.get('search-connector-url')

    if not root:
        raise ZConfig.ConfigurationError(
            "zope.conf has no product config for zeit.connector.")

    return ZopeConnector(dict(
        default=root,
        search=search_root))
