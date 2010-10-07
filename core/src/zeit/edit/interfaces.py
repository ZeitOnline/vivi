# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.interface


class IEditable(zope.interface.Interface):
    """Marker for objects editable through zeit.edit."""
