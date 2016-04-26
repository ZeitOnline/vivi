import json
import lovely.remotetask.interfaces
import zeit.cms.workflow.interfaces
import zope.component


class Status(object):

    def __init__(self, context, request):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        priority = zeit.cms.workflow.interfaces.IPublishPriority(context)
        queue = config['task-queue-%s' % priority]
        self.context = context
        self.tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)
        self.request = request

    def getStatus(self, job):
        return json.dumps(self.tasks.getStatus(int(job)))

    def getError(self, job):
        return json.dumps(self.tasks.getError(int(job)))

    def getResult(self, job):
        return json.dumps(self.tasks.getResult(int(job)))
