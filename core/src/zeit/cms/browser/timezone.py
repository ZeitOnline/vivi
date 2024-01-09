import datetime

import pytz
import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.publisher.interfaces


@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def tzinfo(request):
    return pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).tzinfo
