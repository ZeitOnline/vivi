# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class IRelations(zope.interface.Interface):
    """Utility providing access to relations between objects."""

    def index(obj):
        """Index object and determine relations.

        `obj` must provide the ICMSContent interface.

        """

    def get_relations(obj, relation_name):
        """return objects relating to `obj` with `relation_name`."""


    def add_index(element, multiple=False):
        """add a value index for given element."""
