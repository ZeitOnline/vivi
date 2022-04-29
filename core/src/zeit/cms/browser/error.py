import bugsnag
import six
import six.moves.urllib.parse
import traceback
import zope.error.error
import zope.exceptions.exceptionformatter
import zope.i18n


class ErrorView:

    status = 500

    def __call__(self):
        self.request.response.setStatus(self.status)
        if self.is_xhr:
            # XXX Using a json response would be cleaner.
            self.request.response.setHeader('Content-Type', 'text/plain')
            return self.message
        else:
            return super(ErrorView, self).__call__()

    @property
    def is_xhr(self):
        # Copied from webob.request.Request.is_xhr
        return self.request.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    @property
    def message(self):
        args = getattr(self.context, 'args', None)
        if args:
            message = zope.i18n.translate(
                args[0], context=self.request)
        else:
            message = self.context

        return '%s: %s' % (self.context.__class__.__name__, message)


class ErrorReportingUtility(zope.error.error.RootErrorReportingUtility):

    copy_to_zlog = True

    def raising(self, info, request=None):
        """Adds the (formatted) traceback to the exception object,
        so the ErrorView can display it.

        In Python 2, the exception object does not carry the traceback.
        And since the ErrorView is quite separate from the point where the
        exception is actually caught, we can't use sys.exc_info() either.

        But luckily, the ordering in ZopePublication.handleException()
        works out just fine, so we can enrich the exception object here.
        """

        super(ErrorReportingUtility, self).raising(info, request)
        self._notify_bugsnag(info, request)
        exception = info[1]
        if not isinstance(info[2], six.string_types):
            exception.traceback = getFormattedException(info)
        else:
            exception.traceback = zope.error.error.getPrintable(info[2])

    def _notify_bugsnag(self, info, request):
        url = str(getattr(request, 'URL', ''))
        path = six.moves.urllib.parse.urlparse(url).path if url else None
        username = (self._getUsername(request) or '').split(', ')
        if username:
            user = {'id': username[1], 'name': username[2]}
            if username[3]:
                user['email'] = username[3]
        bugsnag.notify(
            info[1], traceback=info[2], context=path,
            severity='error', user=user)


# copy&paste from zope.error.error to customize the formatter
def getFormattedException(info):
    lines = []
    fmt = ExceptionFormatter()
    for line in fmt.formatException(*info):
        line = zope.error.error.getPrintable(line)
        if not line.endswith('\n'):
            line += '\n'
        lines.append(line)
    return ''.join(lines)


class ExceptionFormatter(
        zope.exceptions.exceptionformatter.TextExceptionFormatter):

    # copy&paste to throw away non-application parts of the traceback.
    def formatException(self, etype, value, tb):
        __exception_formatter__ = 1  # noqa
        result = [self.getPrefix() + '\n']
        limit = self.getLimit()
        n = 0
        inside_app = False
        while tb is not None and (limit is None or n < limit):
            if tb.tb_frame.f_locals.get('__exception_formatter__'):
                # Stop recursion.
                result.append('(Recursive formatException() stopped,'
                              ' trying traceback.format_tb)\n')
                result.extend(traceback.format_tb(tb))
                break
            # patched
            if not inside_app:
                module = tb.tb_frame.f_globals.get('__name__', '')
                if module.startswith('zeit'):
                    inside_app = True
            if inside_app:
                line = self.formatLine(tb)
                result.append(line + '\n')
            # /patched
            tb = tb.tb_next
            n = n + 1
        exc_line = self.formatExceptionOnly(etype, value)
        result.append(self.formatLastLine(exc_line))
        return result
