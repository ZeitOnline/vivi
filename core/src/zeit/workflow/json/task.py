from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import json
import lovely.remotetask.interfaces
import zope.component


class Status(object):

    def __init__(self, context, request):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        queue = config['task-queue-%s' % PRIORITY_DEFAULT]
        self.context = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)
        self.request = request

    def getStatus(self, job):
        return json.dumps(self.context.getStatus(int(job)))

    def getError(self, job):
        return json.dumps(self.context.getError(int(job)))

    def getResult(self, job):
        return json.dumps(self.context.getResult(int(job)))
