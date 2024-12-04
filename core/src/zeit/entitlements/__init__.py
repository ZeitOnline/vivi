import zeit.cms.interfaces

from .interfaces import IAcceptedEntitlements


def accepted(content: zeit.cms.interfaces.ICMSContent) -> set[str]:
    """Returns a set of entitlements, each of which grants access to this content.

    Example: `{'zplus', 'wochenmarkt'}`
    The entitlement identifiers are owned by Premium, see `slug` in
    https://premium.staging.zeit.de/api/0/entitlements (XXX production link?)

    - If the content requires no entitlements (e.g. access==free), returns an empty set
    - access==registration is converted to a synthetic entitlement `{'registration'}`
    """
    return IAcceptedEntitlements(content)()
