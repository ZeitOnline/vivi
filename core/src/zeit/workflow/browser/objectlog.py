# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.interface.common.idatetime import ITZInfo
import zc.resourcelibrary
import zeit.objectlog.interfaces
import zope.authentication.interfaces
import zope.component
import zope.interface


class ProcessForDisplay(object):

    zope.component.adapts(zope.interface.Interface)
    zope.interface.implements(zeit.objectlog.interfaces.ILogProcessor)

    max_entries = 500

    def __init__(self, context):
        pass

    def __call__(self, entries):
        return tuple(entries)[-self.max_entries:]


class ObjectLog(object):

    def groups(self):
        request_timezone = ITZInfo(self.request)
        auth = zope.component.getUtility(
            zope.authentication.interfaces.IAuthentication)
        entries = zeit.objectlog.interfaces.ILog(self.context).get_log()
        groups = {}
        for entry in entries:
            groups.setdefault(entry.time.date(), []).append(entry)
        for date, entries in reversed(sorted(groups.items())):
            items = []
            for entry in reversed(sorted(entries, key=lambda x: x.time)):
                try:
                    principal = auth.getPrincipal(entry.principal)
                except zope.authentication.interfaces.PrincipalLookupError:
                    principal = None
                items.append(dict(
                    display_time=entry.time.astimezone(
                        request_timezone).strftime('%H:%M'),
                    entry=entry,
                    principal=principal.title if principal else ''))
            yield dict(entries=items, display_date=date.strftime('%d.%m.%Y'))

    def __call__(self):
        zc.resourcelibrary.need('zeit.workflow')
        return super(ObjectLog, self).__call__()
