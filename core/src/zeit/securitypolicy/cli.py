import argparse
import json

from zope.securitypolicy.settings import Allow
import transaction
import zope.component.hooks
import zope.securitypolicy.interfaces

import zeit.cms.cli


def dump(filename):
    root = zope.component.hooks.getSite()
    prinrole = zope.securitypolicy.interfaces.IPrincipalRoleManager(root)
    prinperm = zope.securitypolicy.interfaces.IPrincipalPermissionManager(root)
    data = {'roles': [], 'permissions': []}

    for target, principal, setting in prinrole.getPrincipalsAndRoles():
        if setting is not Allow:
            continue
        data['roles'].append((target, principal))

    for target, principal, setting in prinperm.getPrincipalsAndPermissions():
        if setting is not Allow:
            continue
        data['permissions'].append((target, principal))

    json.dump(data, open(filename, 'w'), indent=2)


def load(filename):
    root = zope.component.hooks.getSite()
    prinrole = zope.securitypolicy.interfaces.IPrincipalRoleManager(root)
    prinperm = zope.securitypolicy.interfaces.IPrincipalPermissionManager(root)
    data = json.load(open(filename))

    for target, principal in data['roles']:
        prinrole.assignRoleToPrincipal(target, principal)

    for target, principal in data['permissions']:
        prinperm.grantPermissionToPrincipal(target, principal)

    transaction.commit()


@zeit.cms.cli.runner(principal=zeit.cms.cli.principal_from_args)
def export_import():
    parser = argparse.ArgumentParser(description='Load or dump permissions')
    parser.add_argument('action', choices=['load', 'dump'])
    parser.add_argument('filename')
    options = parser.parse_args()

    if options.action == 'dump':
        dump(options.filename)
    elif options.action == 'load':
        load(options.filename)
