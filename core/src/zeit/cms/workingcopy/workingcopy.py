import grokcore.component as grok
import z3c.traverser.interfaces
import zope.app.security.interfaces
import zope.component
import zope.container.btree
import zope.interface
import zope.publisher.interfaces
import zope.security.interfaces
import zope.security.management
import zope.securitypolicy.interfaces

import zeit.cms.workingcopy.interfaces


@zope.interface.implementer(zeit.cms.workingcopy.interfaces.IWorkingcopy)
class Workingcopy(zope.container.btree.BTreeContainer):
    """The working copy is the area of the CMS where users edit content."""

    _order = ()
    temporary = False  # avoid migration of existing objects

    def __init__(self, temporary=False):
        super().__init__()
        self.temporary = temporary

    def __iter__(self):
        for key in reversed(self._order):
            yield key
        for key in super().__iter__():
            if key in self._order:
                continue
            yield key

    def values(self):
        for key in self:
            yield self[key]

    def __setitem__(self, key, item):
        if not zeit.cms.workingcopy.interfaces.ILocalContent.providedBy(item):
            raise ValueError('Must provide ILocalContent')
        super().__setitem__(key, item)
        self._order += (key,)

    def __delitem__(self, key):
        super().__delitem__(key)
        order = list(self._order)
        try:
            order.remove(key)
        except ValueError:
            pass
        else:
            self._order = tuple(order)


@zope.interface.implementer(zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
class WorkingcopyLocation(zope.container.btree.BTreeContainer):
    """Location for working copies of all users."""

    def getWorkingcopy(self):
        """Get the working copy for the currently logged in user."""
        principal = self._get_principal()
        return self.getWorkingcopyFor(principal)

    def getWorkingcopyFor(self, principal):
        principal_id = principal.id
        try:
            result = self[principal_id]
        except KeyError:
            # User doesn't have a working copy yet, create one
            result = self[principal_id] = Workingcopy()
            perms = zope.securitypolicy.interfaces.IPrincipalPermissionManager(result)
            perms.grantPermissionToPrincipal('zeit.EditContent', principal_id)

            prm = zope.securitypolicy.interfaces.IPrincipalRoleManager(result)
            prm.assignRoleToPrincipal('zeit.Owner', principal_id)
        return result

    def _get_principal(self):
        # Find the current principal. Note that it is possible for there
        # to be more than one principal - in this case we throw an error.
        interaction = zope.security.management.getInteraction()
        principal = None
        for p in interaction.participations:
            if principal is None:
                principal = p.principal
            else:
                raise ValueError('Multiple principals found')
        if principal is None:
            raise ValueError('No principal found')
        return principal


@zope.component.adapter(zope.security.interfaces.IPrincipal)
@zope.interface.implementer(zeit.cms.workingcopy.interfaces.IWorkingcopy)
def principalAdapter(context):
    location = zope.component.getUtility(zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
    return location.getWorkingcopyFor(context)


@grok.adapter(None)
@grok.implementer(zeit.cms.workingcopy.interfaces.IWorkingcopy)
def workingcopy_for_current_principal(ignored):
    # Find the current principal. Note that it is possible for there
    # to be more than one principal - in this case adapting fails
    try:
        interaction = zope.security.management.getInteraction()
    except zope.security.interfaces.NoInteraction:
        return None
    principal = None
    for p in interaction.participations:
        if principal is None:
            principal = p.principal
        else:
            return None
    if principal is None:
        return None
    return zeit.cms.workingcopy.interfaces.IWorkingcopy(principal, None)


@zope.interface.implementer(z3c.traverser.interfaces.IPluggableTraverser)
class WorkingcopyTraverser:
    """Traverses to working copies, creating them on the fly."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        auth = zope.component.getUtility(zope.app.security.interfaces.IAuthentication)
        try:
            principal = auth.getPrincipal(name)
        except zope.app.security.interfaces.PrincipalLookupError:
            raise zope.publisher.interfaces.NotFound(self.context, name, request)
        return zeit.cms.workingcopy.interfaces.IWorkingcopy(principal)
