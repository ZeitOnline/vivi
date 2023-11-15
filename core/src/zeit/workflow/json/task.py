import celery.result
import json


class Status:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getStatus(self, job):
        return json.dumps(self._result(job).state)

    def getError(self, job):
        return json.dumps(self._result(job).failed())

    def getResult(self, job):
        return json.dumps(self._result(job).get())

    def _result(self, job):
        return celery.result.AsyncResult(job)
