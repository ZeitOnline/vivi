# Copyright (c) 2009-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import json
import lovely.remotetask.interfaces
import zope.component


class Status(object):

    def __init__(self, context, request):
        self.context = zope.component.getUtility(
            lovely.remotetask.interfaces.ITaskService, 'general')
        self.request = request

    def getStatus(self, job):
        return json.dumps(self.context.getStatus(int(job)))

    def getError(self, job):
        return json.dumps(self.context.getError(int(job)))

    def getResult(self, job):
        return json.dumps(self.context.getResult(int(job)))
