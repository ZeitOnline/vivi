from zeit.objectlog.i18n import MessageFactory as _
import zc.sourcefactory.contextual
import zeit.objectlog.interfaces
import zope.app.form.browser.interfaces
import zope.i18n
import zope.interface.common.idatetime


class LogEntrySource(
        zc.sourcefactory.contextual.BasicContextualSourceFactory):

    def getValues(self, context):
        log = zeit.objectlog.interfaces.ILog(context)
        return log.get_log()

    def createTerm(self, context, source, value, title, token, request):
        # We got to create the title here as we haven't got the request in
        # `getTitle` :(

        if value.principal is None:
            principal = _('System')
        else:
            p_source = zeit.objectlog.interfaces.ILogEntry['principal'].source
            principal_terms = zope.component.getMultiAdapter(
                (p_source, request), zope.app.form.browser.interfaces.ITerms)
            try:
                principal = principal_terms.getTerm(value.principal).title
            except LookupError:
                principal = value.principal

        formatter = request.locale.dates.getFormatter('dateTime', 'medium')
        tzinfo = zope.interface.common.idatetime.ITZInfo(request, None)
        time = value.time
        if tzinfo is not None:
            time = time.astimezone(tzinfo)
        time = formatter.format(time)

        message = zope.i18n.translate(value.message, context=request)

        title = _("${time} [${principal}]: ${message}",
                  mapping=dict(
                      time=time,
                      principal_id=value.principal,
                      principal=principal,
                      message=message))

        return super().createTerm(
            context, source, value, title, token, request)
