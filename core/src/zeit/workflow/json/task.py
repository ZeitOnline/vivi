import json

import celery.result


class Status:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getStatus(self, jobs):
        jobs = jobs.split(',')
        results = (self._result(job) for job in jobs)
        return json.dumps(self._get_joined_state(results))

    # This is only used in a smoketest
    def getResult(self, jobs):
        jobs = jobs.split(',')
        results = (self._result(job) for job in jobs)
        if self._get_joined_state(results) == 'SUCCESS':
            return ', '.join((result.get() for result in results))
        else:
            return ', '.join((result.traceback for result in results if result.state == 'FAILURE'))

    def _get_joined_state(self, results):
        all_success = True
        for result in results:
            if result.state == 'FAILURE':
                return 'FAILURE'
            if result.state != 'SUCCESS':
                all_success = False
        return 'SUCCESS' if all_success else 'PENDING'

    def _result(self, job):
        return celery.result.AsyncResult(job)
