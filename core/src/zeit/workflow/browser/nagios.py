from zeit.cms.workflow.interfaces import PRIORITY_DEFAULT
import lovely.remotetask.interfaces
import zope.component


class TaskQueueLength(object):

    def __call__(self):
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.workflow')
        queue = config['task-queue-%s' % PRIORITY_DEFAULT]
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, name=queue)
        # note: hasJobsWaiting() also schedules any pending cronjobs,
        # so it can have influence on our result
        if not tasks.hasJobsWaiting():
            return '0'
        else:
            # XXX this is an implementation detail, but going through the
            # interface would entail filtering *all* jobs for those that have
            # the status QUEUED, and that just does not perform
            return str(len(tasks._queue))
