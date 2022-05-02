from io import BytesIO


class MemoryFile:

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

    def __enter__(self):
        return self.data.__enter__()

    def __exit__(self, *args):
        self.close()

    # pickle support, since zeit.web wants to put these in a dogpile.cache
    data = None

    def __getstate__(self):
        return {'data': self.data}
