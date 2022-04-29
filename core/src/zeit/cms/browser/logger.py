import bugsnag
import json
import logging
import six.moves.urllib.parse
import zeit.cms.browser.view
import zope.component
import zope.error.interfaces


log = logging.getLogger('JavaScript')


class JSONLog(zeit.cms.browser.view.JSON):

    # XXX It would be even nicer to convert the JS traceback to Python and
    # then simply use IErrorReportingUtility.raising().
    def json(self):
        decoded = json.loads(self.request.bodyStream.read(
            int(self.request['CONTENT_LENGTH'])))
        message = '\n'.join(str(x) for x in decoded['message'])

        # XXX Ignore errors triggered by Firefox bug where a
        # mousemove(target=#newtab-vertical-margin) event, which actually
        # belongs to the FF-UI, ends up on the page.
        if 'Permission denied to access property "type"' in message:
            return {}

        log_func = getattr(log, decoded['level'].lower())

        error_reporting_util = zope.component.getUtility(
            zope.error.interfaces.IErrorReportingUtility)
        user = (
            error_reporting_util._getUsername(self.request) or '').split(', ')
        if user:
            user = {'id': user[1], 'name': user[2], 'email': user[3]}
        url = decoded['url']
        message = '%s (%s) %s' % (url, user['id'], message)
        # XXX should we populate Python's logmessage timestamp from json?
        log_func(message)

        path = six.moves.urllib.parse.urlparse(url).path if url else None
        js_error = decoded['message'][0]
        bugsnag.notify(
            JavaScriptError(js_error), context=path, severity='error',
            user=user, grouping_hash=js_error)

        return {}


class JavaScriptError(Exception):
    pass
