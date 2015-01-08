
class ProcessingError(object):

    def __call__(self):
        self.request.response.setStatus(500)
        return self.index()
