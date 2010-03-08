# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import persistent
import zeit.brightcove.interfaces
import zope.interface
import zope.container.contained


class Video(persistent.Persistent,
            zope.container.contained.Contained):

    #zope.interface.implements(zeit.brightcove.interfaces.IVideo)
    pass
