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
