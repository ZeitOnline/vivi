import logging
import lxml.etree
import lxml.objectify
import copyreg


log = logging.getLogger(__name__)


def treeFactory(state):
    """Un-Pickle factory."""
    try:
        return lxml.objectify.fromstring(state)
    except Exception as e:
        log.error('Error during unpickling', exc_info=True)
        return lxml.objectify.fromstring(
            '<error><!-- XML-FEHLER: %s\n\n%s\n\n--></error>' % (e, state))


copyreg.constructor(treeFactory)


def reduceObjectifiedElement(object):
    """Reduce function for lxml.objectify trees.
    See http://docs.python.org/lib/pickle-protocol.html for details.
    """
    state = lxml.etree.tostring(object.getroottree())
    return (treeFactory, (state, ))


copyreg.pickle(
    lxml.objectify.ObjectifiedElement, reduceObjectifiedElement, treeFactory)
