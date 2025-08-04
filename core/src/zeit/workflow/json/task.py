import json

import celery.result


class Status:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getStatus(self, job):
        return json.dumps(self._result(job).state)

    def getResult(self, job):
        result = self._result(job)
        if result.state == 'SUCCESS':
            return result.get()
        else:
            return result.traceback

    def _result(self, job):
        return celery.result.AsyncResult(job)
