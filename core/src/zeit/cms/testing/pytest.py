def copy_inherited_functions(base, locals):
    """pytest annotates the test function object with data, e.g. required
    fixtures. Normal inheritance means that there is only *one* function object
    (in the base class), which means for example that subclasses cannot specify
    different layers, since they would all aggregate on that one function
    object, which would be completely wrong.

    Usage: copy_inherited_functions(BaseClass, locals())
    """

    def make_delegate(name):
        def delegate(self):
            return getattr(super(type(self), self), name)()

        return delegate

    for name in dir(base):
        if not name.startswith('test_'):
            continue
        locals[name] = make_delegate(name)
