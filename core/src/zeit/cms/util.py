from io import BytesIO


class MemoryFile(object):

    def __init__(self, value=None):
        # XXX Even though the signature is BytesIO.__init__([initial_bytes]),
        # it behaves differently when passed no argument.
        if value is not None:
            self.data = BytesIO(value)
        else:
            self.data = BytesIO()

    def __getattr__(self, name):
        return getattr(self.data, name)

    def close(self):
        self.seek(0)
