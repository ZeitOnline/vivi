import zope.i18nmessageid
import zope.interface
import zope.schema


_ = zope.i18nmessageid.MessageFactory('zeit.cms')


class ILockFormSchema(zope.interface.Interface):
    locked = zope.schema.Bool(title=_('Locked'), readonly=True)

    locker = zope.schema.TextLine(title=_('Locker'), required=False, readonly=True)

    locked_until = zope.schema.Datetime(title=_('Locked until'), required=False, readonly=True)
