# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class ISearchPreferences(zope.interface.Interface):

    show_extended = zope.schema.Bool(
        title=u"Show extended search",
        default=False)
