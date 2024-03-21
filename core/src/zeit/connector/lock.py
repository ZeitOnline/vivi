from zope.component import queryUtility


def lock_is_foreign(principal):
    try:
        import zope.authentication.interfaces  # UI-only dependency

        authentication = queryUtility(zope.authentication.interfaces.IAuthentication)
    except ImportError:
        return True
    try:
        authentication.getPrincipal(principal)
    except zope.authentication.interfaces.PrincipalLookupError:
        return True
    return False
