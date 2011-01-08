# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component.zcml
import zope.security.zcml
import zope.security.permission
import zope.security.interfaces

import zeit.cms.interfaces


class IEditPermissionDirective(zope.security.zcml.IPermissionDirective):
    """Define a new edit permission.

    Edit permissions are automatically forbidden in the repository.

    """


def edit_permission(_context, id, title, description=''):
    permission = zope.security.permission.Permission(id, title, description)
    zope.component.zcml.utility(
        _context, zeit.cms.interfaces.IEditPermission, permission, name=id)
