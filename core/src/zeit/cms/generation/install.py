import lovely.remotetask
import lovely.remotetask.interfaces
import lovely.remotetask.processor
import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.generation
import zeit.cms.relation.relation
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.workingcopy.workingcopy
import zope.component
import zope.error.interfaces


def installLocalUtility(root, factory, name, interface, utility_name=u''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def installGeneralTaskService():
    _install_task_service('tasks.general', 'general', max_threads=5)


def installHighPriorityTaskService():
    _install_task_service('tasks.highprio', 'highprio', max_threads=5)


def installLowPriorityTaskService():
    _install_task_service('tasks.lowprio', 'lowprio', max_threads=1)


def installHomepageTaskService():
    _install_task_service('tasks.homepage', 'homepage', max_threads=1)


def installEventTaskService():
    _install_task_service('tasks.event', 'events', max_threads=1)


def installSolrTaskService():
    _install_task_service('tasks.solr', 'solr', max_threads=1)


def _install_task_service(name, utility_name, max_threads):
    site_manager = zope.component.getSiteManager()
    tasks = installLocalUtility(
        site_manager, lovely.remotetask.TaskService, name,
        lovely.remotetask.interfaces.ITaskService, utility_name=utility_name)
    # Use MultiProcessor with 1 Thread because it handles pulling from the
    # queue differently than the SingleProcessor.
    tasks.processorFactory = lovely.remotetask.processor.MultiProcessor
    tasks.processorArguments = {'maxThreads': max_threads}


def installRelations():
    site_manager = zope.component.getSiteManager()
    relations = installLocalUtility(
        site_manager,
        zeit.cms.relation.relation.Relations,
        'relations',
        zeit.cms.relation.interfaces.IRelations)
    relations.add_index(
        zeit.cms.relation.relation.referenced_by, multiple=True)


def installErrorReportingUtility(root):
    zope.app.appsetup.bootstrap.addConfigureUtility(
        root, zope.error.interfaces.IErrorReportingUtility, '',
        zeit.cms.browser.error.ErrorReportingUtility)


def install(root):
    installErrorReportingUtility(root)
    installLocalUtility(
        root, zeit.cms.repository.repository.repositoryFactory,
        'repository', zeit.cms.repository.interfaces.IRepository)
    installLocalUtility(
        root, zeit.cms.workingcopy.workingcopy.WorkingcopyLocation,
        'workingcopy', zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
    installLocalUtility(
        root, zeit.cms.content.template.TemplateManagerContainer,
        'templates', zeit.cms.content.interfaces.ITemplateManagerContainer)
    installGeneralTaskService()
    installEventTaskService()
    installSolrTaskService()
    installHighPriorityTaskService()
    installLowPriorityTaskService()
    installHomepageTaskService()
    installRelations()


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
