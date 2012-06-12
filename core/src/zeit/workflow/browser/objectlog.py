# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zc.resourcelibrary
import zeit.objectlog.interfaces
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
        entries = zeit.objectlog.interfaces.ILog(self.context).get_log()
        groups = {}
        for entry in entries:
            groups.setdefault(entry.time.date(), []).append(entry)
        for date, entries in sorted(groups.items()):
            yield dict(
                display_date=date.strftime('%d.%m.%Y'),
                entries=[dict(
                        display_time=entry.time.strftime('%H:%M'),
                        entry=entry,
                        ) for entry in entries],
                )

    def __call__(self):
        zc.resourcelibrary.need('zeit.workflow')
        return super(ObjectLog, self).__call__()
