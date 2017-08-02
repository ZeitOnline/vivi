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
    state = lxml.etree.tostring(object.getroottree())
    return (treeFactory, (state, ))
copy_reg.pickle(
    lxml.objectify.ObjectifiedElement, reduceObjectifiedElement, treeFactory)
