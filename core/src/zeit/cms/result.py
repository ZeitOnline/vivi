import zeit.cms.interfaces
import zope.interface


class Result(list):
    """A list with additional property ``hits``."""

    zope.interface.implements(zeit.cms.interfaces.IResult)

    hits = 0
