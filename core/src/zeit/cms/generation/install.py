# Copyright (c) 2007-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import lovely.remotetask
import lovely.remotetask.processor
import lovely.remotetask.interfaces

import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.generation
import zeit.cms.relation.relation
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.syndication.feed
import zeit.cms.workingcopy.workingcopy


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


def installEventTaskService():
    site_manager = zope.component.getSiteManager()
    tasks = installLocalUtility(
        site_manager, lovely.remotetask.TaskService, 'tasks.event',
        lovely.remotetask.interfaces.ITaskService, utility_name='events')
    # Use MultiProcessor with 1 Thread because it handles pulling from the
    # queue differently than the SingleProcessor.
    tasks.processorFactory = lovely.remotetask.processor.MultiProcessor
    tasks.processorArguments = {'maxThreads': 1}


def installRelations():
    site_manager = zope.component.getSiteManager()
    relations = installLocalUtility(
        site_manager,
        zeit.cms.relation.relation.Relations,
        'relations',
        zeit.cms.relation.interfaces.IRelations)
    relations.add_index(
        zeit.cms.relation.relation.referenced_by, multiple=True)


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
    installLocalUtility(
        root, zeit.cms.tagging.whitelist.Whitelist,
        'tag-whitelist', zeit.cms.tagging.interfaces.IWhitelist)
    installGeneralTaskService()
    installEventTaskService()
    installRelations()


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
