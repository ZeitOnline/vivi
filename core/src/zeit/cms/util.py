import cStringIO


class MemoryFile(object):

    def __init__(self, value=None):
        # XXX Even though the signature is StringIO.__init__(buf=''), it
        # behaves differently when passed no argument.
        if value is not None:
            self.data = cStringIO.StringIO(value)
        else:
            self.data = cStringIO.StringIO()

    def __getattr__(self, name):
        return getattr(self.data, name)

    def close(self):
        self.seek(0)
