from zope.component import getUtility


try:
    import zope.authentication.interfaces  # UI-only dependency
except ImportError:
    HAVE_AUTH = False
else:
    HAVE_AUTH = True


def lock_is_foreign(principal):
    if not HAVE_AUTH:
        return True
    try:
        authentication = getUtility(zope.authentication.interfaces.IAuthentication)
    except LookupError:
        return True
    try:
        authentication.getPrincipal(principal)
    except zope.authentication.interfaces.PrincipalLookupError:
        return True
    return False
