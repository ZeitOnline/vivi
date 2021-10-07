import os.path
import zope.app.appsetup.product


class HealthCheck:

    def __call__(self):
        config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')
        stopfile = config.get('stopfile')
        if stopfile and os.path.exists(stopfile):
            self.request.response.setStatus(500)
            return 'fail: stopfile %s present' % stopfile
        return 'OK'
