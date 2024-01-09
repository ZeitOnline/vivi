import zeit.cms.clipboard.interfaces
import zeit.cms.workingcopy.interfaces


class IGhost(
    zeit.cms.workingcopy.interfaces.ILocalContent, zeit.cms.clipboard.interfaces.IObjectReference
):
    """Marker interface to distinguish ghosts from "normal" local content
    objects.
    """
