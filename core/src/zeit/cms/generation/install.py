import zope.app.appsetup.bootstrap
import zope.component
import zope.error.interfaces
import zope.principalannotation.interfaces
import zope.principalannotation.utility

import zeit.authentication.azure
import zeit.cms.browser.error
import zeit.cms.generation
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.retractlog.retractlog
import zeit.cms.workingcopy.workingcopy


def installLocalUtility(root, factory, name, interface, utility_name=''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def install(root):
    zope.app.appsetup.bootstrap.addConfigureUtility(
        root,
        zope.principalannotation.interfaces.IPrincipalAnnotationUtility,
        'PrincipalAnnotation',
        zope.principalannotation.utility.PrincipalAnnotationUtility,
    )
    installLocalUtility(
        root,
        zeit.cms.repository.repository.repositoryFactory,
        'repository',
        zeit.cms.repository.interfaces.IRepository,
    )
    installLocalUtility(
        root,
        zeit.cms.workingcopy.workingcopy.WorkingcopyLocation,
        'workingcopy',
        zeit.cms.workingcopy.interfaces.IWorkingcopyLocation,
    )
    root['retractlog'] = zeit.cms.retractlog.retractlog.RetractLog()
    installLocalUtility(
        root,
        zeit.authentication.azure.PersistentTokenCache,
        'azure-token-cache',
        zeit.authentication.azure.ITokenCache,
    )


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
