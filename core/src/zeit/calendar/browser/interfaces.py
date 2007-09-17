# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema


class ILastView(zope.interface.Interface):

    last_view = zope.schema.ASCIILine(
        title=u"The last calendar view the user has visited.")
