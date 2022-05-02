from datetime import datetime, timedelta
from zope.cachedescriptors.property import Lazy as cachedproperty
import re
import zeit.vgwort.interfaces
import zope.component


class Status:

    @cachedproperty
    def reported_on(self):
        return self._format_date(self.info.reported_on)

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

    @cachedproperty
    def date_first_released(self):
        info = zeit.cms.workflow.interfaces.IPublishInfo(self.context)
        return info.date_first_released

    @cachedproperty
    def to_report_on(self):
        dfr = self.date_first_released
        result = datetime(dfr.year, dfr.month, dfr.day) + timedelta(days=8)
        now = datetime.now()
        if result < now:
            result = datetime(now.year, now.month, now.day)
        return result.strftime('%d.%m.%Y')

    def _format_date(self, date):
        if not date:
            return None
        return self._date_formatter.format(date)

    @cachedproperty
    def _date_formatter(self):
        return self.request.locale.dates.getFormatter('dateTime', 'medium')

    def has_permission(self, permission):
        return self.request.interaction.checkPermission(
            permission, self.context)


class Retry(zeit.cms.browser.view.Base):

    def __call__(self):
        if self.request.method != 'POST':
            return 405, 'Only POST supported'
        source = zope.component.getUtility(
            zeit.vgwort.interfaces.IReportableContentSource)
        source.mark_todo(zope.security.proxy.getObject(self.context))
        return self.redirect(self.url('vgwort.html'))
