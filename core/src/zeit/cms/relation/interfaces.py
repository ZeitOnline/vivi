# Copyright (c) 2008-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class IRelations(zope.interface.Interface):
    """Utility providing access to relations between objects."""

    def index(obj):
        """Index object and determine relations.

        `obj` must provide the ICMSContent interface.

        """

    def get_relations(obj):
        """return objects that reference `obj`."""

    def add_index(element, multiple=False):
        """add a value index for given element."""


class IReferences(zope.interface.Interface):
    """An adapter that returns a list of objects that are referenced by the
    context. This is the client-side entry point, it delegates to all
    IReferenceProviders."""


class IReferenceProvider(zope.interface.Interface):
    """An adapter that returns a list of objects that are referenced by the
    context. If you want to provide additional referenced objects, implement
    this interface."""
