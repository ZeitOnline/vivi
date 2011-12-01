# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import copy_reg
import hashlib
import lxml.etree
import lxml.objectify
import threading
import zope.app.publication.interfaces
import zope.testing.cleanup


class Refs(threading.local):

    def __init__(self):
        self.refs = {}

_refs = Refs()
zope.testing.cleanup.addCleanUp(_refs.refs.clear)


def hash_state(state):
    return hashlib.sha224(state).digest()


@zope.component.adapter(zope.app.publication.interfaces.IEndRequestEvent)
def clean_refs(event, _refs=_refs):
    _refs.refs.clear()


def treeFactory(state, _refs=_refs):
    """Un-Pickle factory."""
    hash_ = hash_state(state)
    tree = _refs.refs.get(hash_)
    if tree is None:
        tree = lxml.objectify.fromstring(state)
        _refs.refs[hash_] = tree
    return tree

copy_reg.constructor(treeFactory)


def reduceObjectifiedElement(object):
    """Reduce function for lxml.objectify trees.

    See http://docs.python.org/lib/pickle-protocol.html for details.
    """

    root_tree = object.getroottree()
    state = lxml.etree.tostring(root_tree)
    _refs.refs[hash_state(state)] = root_tree.getroot()
    return (treeFactory, (state, ))


copy_reg.pickle(lxml.objectify.ObjectifiedElement,
                reduceObjectifiedElement,
                treeFactory)
