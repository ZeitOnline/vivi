import pendulum
import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.publisher.interfaces


@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def tzinfo(request):
    tz = pendulum.timezone('Europe/Berlin')
    # XXX zc.i18n relies on this `pytz` implementation detail,
    # even though ITZInfo does not support it.
    tz.localize = lambda dt, **kw: dt.replace(tzinfo=tz)
    return tz
