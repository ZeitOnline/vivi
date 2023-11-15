import zeit.cms.browser.error
import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.generation
import zeit.cms.relation.relation
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.retractlog.retractlog
import zeit.cms.workingcopy.workingcopy
import zope.component
import zope.error.interfaces


def installLocalUtility(root, factory, name, interface, utility_name=''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def installRelations():
    site_manager = zope.component.getSiteManager()
    relations = installLocalUtility(
        site_manager,
        zeit.cms.relation.relation.Relations,
        'relations',
        zeit.cms.relation.interfaces.IRelations,
    )
    relations.add_index(zeit.cms.relation.relation.referenced_by, multiple=True)


def installErrorReportingUtility(root):
    zope.app.appsetup.bootstrap.addConfigureUtility(
        root,
        zope.error.interfaces.IErrorReportingUtility,
        '',
        zeit.cms.browser.error.ErrorReportingUtility,
    )


def install(root):
    installErrorReportingUtility(root)
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
    installLocalUtility(
        root,
        zeit.cms.content.template.TemplateManagerContainer,
        'templates',
        zeit.cms.content.interfaces.ITemplateManagerContainer,
    )
    root['retractlog'] = zeit.cms.retractlog.retractlog.RetractLog()
    installRelations()


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
