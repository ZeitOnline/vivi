# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import pytz

import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.publisher.interfaces.browser


@zope.component.adapter(zope.publisher.interfaces.browser.IBrowserRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def tzinfo(request):
     return pytz.timezone('Europe/Berlin')
