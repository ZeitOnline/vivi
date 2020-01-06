import lxml.etree
import lxml.objectify
import six.moves.copyreg


def treeFactory(state):
    """Un-Pickle factory."""
    try:
        return lxml.objectify.fromstring(state)
    except Exception as e:
        return lxml.objectify.fromstring(
            '<error><!-- XML-FEHLER: %s\n\n%s\n\n--></error>' % (e, state))


six.moves.copyreg.constructor(treeFactory)


def reduceObjectifiedElement(object):
    """Reduce function for lxml.objectify trees.
    See http://docs.python.org/lib/pickle-protocol.html for details.
    """
    state = lxml.etree.tostring(object.getroottree())
    return (treeFactory, (state, ))


six.moves.copyreg.pickle(
    lxml.objectify.ObjectifiedElement, reduceObjectifiedElement, treeFactory)
