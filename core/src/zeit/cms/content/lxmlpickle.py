import copy_reg
import lxml.etree
import lxml.objectify


def treeFactory(state):
    """Un-Pickle factory."""
    try:
        return lxml.objectify.fromstring(state)
    except Exception as e:
        return lxml.objectify.fromstring(
            '<error><!-- XML-FEHLER: %s\n\n%s\n\n--></error>' % (e, state))
copy_reg.constructor(treeFactory)


def reduceObjectifiedElement(object):
    """Reduce function for lxml.objectify trees.
    See http://docs.python.org/lib/pickle-protocol.html for details.
    """
    state = lxml.etree.tostring(object.getroottree())
    return (treeFactory, (state, ))
copy_reg.pickle(
    lxml.objectify.ObjectifiedElement, reduceObjectifiedElement, treeFactory)
