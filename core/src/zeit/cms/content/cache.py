class writeabledict(dict):
    """dict with all (especially write) methods allowed by security"""


def content_cache(context, doc_iface, name, factory=writeabledict):
    parent = doc_iface(context)
    return parent.cache.setdefault(name, factory())


def cached_on_content(
        doc_iface, attr=None, keyfunc=lambda x: x, factory=writeabledict):
    """ Decorator to cache the results of the function in a dictionary
        on the centerpage.  The dictionary keys are built using the optional
        `keyfunc`, which is called with `self` as a single argument. """
    def decorator(fn):
        def wrapper(self, *args, **kw):
            cache = content_cache(self, doc_iface, attr or fn.__name__)
            key = keyfunc(self)
            if key not in cache:
                cache[key] = fn(self, *args, **kw)
            return cache[key]
        return wrapper
    return decorator
