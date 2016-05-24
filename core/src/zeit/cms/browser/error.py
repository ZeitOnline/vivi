import bugsnag
import urlparse
import zope.error.error
import zope.i18n


class ErrorView(object):

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
        if not isinstance(info[2], basestring):
            exception.traceback = zope.error.error.getFormattedException(info)
        else:
            exception.traceback = zope.error.error.getPrintable(info[2])

    def _notify_bugsnag(self, info, request):
        url = str(getattr(request, 'URL', ''))
        path = urlparse.urlparse(url).path if url else None
        username = (self._getUsername(request) or '').split(', ')
        if username:
            user = {'id': username[1], 'name': username[2]}
            if username[3]:
                user['email'] = username[3]
        bugsnag.notify(
            info[1], traceback=info[2], context=path,
            severity='error', user=user)
