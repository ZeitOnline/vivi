"""Wraps zope product-config so it does not break when the package has no configuration at all"""

import zope.app.appsetup.product


def get(pkg, key, default=None):
    return package(pkg).get(key, default)


def required(pkg, key):
    return package(pkg)[key]


def package(pkg):
    config = zope.app.appsetup.product.getProductConfiguration(pkg)
    if config is None:
        config = {}
        zope.app.appsetup.product.setProductConfiguration(pkg, config)
    return config


def set(pkg, key, value):
    package(pkg)[key] = value
