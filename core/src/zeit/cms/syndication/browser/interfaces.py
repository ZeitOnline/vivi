# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class ISyndicationManagerView(zope.interface.Interface):

    manager = zope.interface.Attribute("Syndicaiton Manager.")
