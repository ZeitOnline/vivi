import ast
import bugsnag
import bugsnag.wsgi.middleware
import webob


# XXX copy&paste to allow disabling overwriting the user id with the IP address
class BugsnagMiddleware:

    def __init__(self, application, user_from_ip):
        bugsnag.before_notify(self.add_wsgi_request_data_to_notification)
        self.application = application
        self.user_from_ip = user_from_ip

    def __call__(self, environ, start_response):
        return bugsnag.wsgi.middleware.WrappedWSGIApp(
            self.application, environ, start_response)

    def add_wsgi_request_data_to_notification(self, notification):
        if not hasattr(notification.request_config, 'wsgi_environ'):
            return

        environ = notification.request_config.wsgi_environ
        request = webob.Request(environ)

        notification.context = '%s %s' % (
            request.method, bugsnag.wsgi.request_path(environ))
        if self.user_from_ip:
            notification.set_user(id=request.client_addr)
        notification.add_tab('request', {
            'url': request.path_url,
            'headers': dict(request.headers),
            'cookies': dict(request.cookies),
            'params': dict(request.params),
        })
        notification.add_tab('environment', dict(request.environ))


# bugsnag itself does not provide a paste filter factory
def bugsnag_filter(global_conf, **local_conf):
    user_from_ip = ast.literal_eval(
        local_conf.pop('set_user_id_to_client_ip', 'True'))

    if 'notify_release_stages' in local_conf:
        local_conf['notify_release_stages'] = local_conf[
            'notify_release_stages'].split(',')
    bugsnag.configure(**local_conf)

    def bugsnag_filter(app):
        return BugsnagMiddleware(app, user_from_ip)
    return bugsnag_filter
