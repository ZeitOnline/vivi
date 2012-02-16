# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

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
import zope.component.interfaces
import zope.error.interfaces


def installLocalUtility(root, factory, name, interface, utility_name=u''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def installGeneralTaskService():
    site_manager = zope.component.getSiteManager()
    tasks = installLocalUtility(
        site_manager, lovely.remotetask.TaskService, 'tasks.general',
        lovely.remotetask.interfaces.ITaskService, utility_name='general')
    # Use MultiProcessor for parallel processing.
    tasks.processorFactory = lovely.remotetask.processor.MultiProcessor


def _install_serial_task_service(name, utility_name):
    site_manager = zope.component.getSiteManager()
    tasks = installLocalUtility(
        site_manager, lovely.remotetask.TaskService, name,
        lovely.remotetask.interfaces.ITaskService, utility_name=utility_name)
    # Use MultiProcessor with 1 Thread because it handles pulling from the
    # queue differently than the SingleProcessor.
    tasks.processorFactory = lovely.remotetask.processor.MultiProcessor
    tasks.processorArguments = {'maxThreads': 1}


def installEventTaskService():
    _install_serial_task_service('tasks.event', 'events')


def installLowPriorityTaskService():
    _install_serial_task_service('tasks.lowprio', 'lowprio')


def installRelations():
    site_manager = zope.component.getSiteManager()
    relations = installLocalUtility(
        site_manager,
        zeit.cms.relation.relation.Relations,
        'relations',
        zeit.cms.relation.interfaces.IRelations)
    relations.add_index(
        zeit.cms.relation.relation.referenced_by, multiple=True)


@zope.component.adapter(
    zope.error.interfaces.IErrorReportingUtility,
    zope.component.interfaces.IRegistered)
def configure_error_utility(errUtility, event):
    # The error utility is installed by zope.app.appsetup. This is a point in
    # time that works for making our configuration wishes heard.
    errUtility.copy_to_zlog = True


def install(root):
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
    installLowPriorityTaskService()
    installRelations()


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
