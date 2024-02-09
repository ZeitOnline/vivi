import copyreg
import logging

import lxml.etree
import lxml.objectify


log = logging.getLogger(__name__)


def deserialize(state):
    try:
        return lxml.etree.fromstring(state)
    except Exception as e:
        log.error('Error during unpickling', exc_info=True)
        return lxml.etree.fromstring('<error><!-- XML-FEHLER: %s\n\n%s\n\n--></error>' % (e, state))


copyreg.constructor(deserialize)


def serialize(obj):
    """Reduce function for lxml trees.
    See http://docs.python.org/lib/pickle-protocol.html for details.
    """
    state = lxml.etree.tostring(obj.getroottree())
    return (
        deserialize,
        (state,),
    )


copyreg.pickle(lxml.etree._Element, serialize)

# BBB
treeFactory = deserialize
copyreg.pickle(lxml.objectify.ObjectifiedElement, serialize)
