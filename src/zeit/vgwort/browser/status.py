from zope.cachedescriptors.property import Lazy as cachedproperty
import re
import zeit.vgwort.interfaces


class Status(object):

    @cachedproperty
    def reported_on(self):
        if not self.info.reported_on:
            return None
        date_formatter = self.request.locale.dates.getFormatter(
            'dateTime', 'medium')
        return date_formatter.format(self.info.reported_on)

    @cachedproperty
    def reported_error(self):
        msg = self.info.reported_error
        if not msg:
            return None
        if 'errormsg' in msg:
            # Prettify spelling of the most common error, "text is too short"
            msg = re.sub(r'\(detail\).*errormsg = "', '', msg, flags=re.DOTALL)
            msg = re.sub(r'".*$', '', msg, flags=re.DOTALL)
        return msg

    @cachedproperty
    def info(self):
        return zeit.vgwort.interfaces.IReportInfo(self.context)
