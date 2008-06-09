# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import copy_reg

import lxml.etree
import lxml.objectify


def treeFactory(state):
    """Un-Pickle factory."""
    return lxml.objectify.fromstring(state)

copy_reg.constructor(treeFactory)


def reduceObjectifiedElement(object):
    """Reduce function for lxml.objectify trees.

    See http://docs.python.org/lib/pickle-protocol.html for details.
    """
    return (treeFactory,
            (lxml.etree.tostring(object.getroottree()), ))

copy_reg.pickle(lxml.objectify.ObjectifiedElement,
                reduceObjectifiedElement,
                treeFactory)
