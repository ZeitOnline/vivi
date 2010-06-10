# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""
Extend suds to handle parameters passed as attributes of the request element.

There seems to be no other way than monkey-patching right into the middle of
things, changes from the copied code are marked 'PATCH:'.
"""

from suds.bindings.document import log
from suds.sax.attribute import Attribute
import suds.bindings.document


### patching suds.bindings.document.Document ------------------------------


def bodycontent(self, method, args, kwargs):
    #
    # The I{wrapped} vs I{bare} style is detected in 2 ways.
    # If there is 2+ parts in the message then it is I{bare}.
    # If there is only (1) part and that part resolves to a builtin then
    # it is I{bare}.  Otherwise, it is I{wrapped}.
    #
    if not len(method.soap.input.body.parts):
        return ()
    wrapped = method.soap.input.body.wrapped
    if wrapped:
        pts = self.bodypart_types(method)
        root = self.document(pts[0])
    else:
        root = []
    n = 0
    for pd in patched_param_defs(self, method):
        if n < len(args):
            value = args[n]
        else:
            value = kwargs.get(pd[0])
        n += 1
        # PATCH: handle attributes
        if not pd[2]:
            # this is the upstream default, append an element
            p = self.mkparam(method, pd, value)
            if p is None:
                continue
            if not wrapped:
                ns = pd[1].namespace('ns0')
                p.setPrefix(ns[0], ns[1])
            root.append(p)
        else:
            root.attributes.append(Attribute(pd[0], value))

    return root


def patched_param_defs(self, method):
    #
    # Get parameter definitions for document literal.
    # The I{wrapped} vs I{bare} style is detected in 2 ways.
    # If there is 2+ parts in the message then it is I{bare}.
    # If there is only (1) part and that part resolves to a builtin then
    # it is I{bare}.  Otherwise, it is I{wrapped}.
    #
    pts = self.bodypart_types(method)
    wrapped = method.soap.input.body.wrapped
    if not wrapped:
        return pts
    result = []
    # wrapped
    for p in pts:
        resolved = p[1].resolve()
        for child, ancestry in resolved:
            # PATCH: include attributes as params
            # if child.isattr():
            #     continue
            if self.bychoice(ancestry):
                log.debug(
                    '%s\ncontained by <choice/>, excluded as param for %s()',
                    child,
                    method.name)
                continue
            # PATCH: store param type (element/attribute)
            result.append((child.name, child, child.isattr()))
    return result


suds.bindings.document.Document.bodycontent = bodycontent
