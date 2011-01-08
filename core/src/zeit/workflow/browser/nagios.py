# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import lovely.remotetask.interfaces
import zope.component


class TaskQueueLength(object):

    def __call__(self):
        tasks = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        # note: hasJobsWaiting() also schedules any pending cronjobs,
        # so it can have influence on our result
        if not tasks.hasJobsWaiting():
            return '0'
        else:
            # XXX this is an implementation detail, but going through the
            # interface would entail filtering *all* jobs for those that have
            # the status QUEUED, and that just does not perform
            return str(len(tasks._queue))
