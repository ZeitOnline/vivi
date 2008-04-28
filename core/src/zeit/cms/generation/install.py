# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.component

import lovely.remotetask
import lovely.remotetask.interfaces

import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.generation
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.workingcopy.workingcopy


def installLocalUtility(root, factory, name, interface, utility_name=u''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def installTaskService():
    site_manager = zope.component.getSiteManager()
    installLocalUtility(
        site_manager, lovely.remotetask.TaskService, 'tasks.general',
        lovely.remotetask.interfaces.ITaskService, utility_name='general')


def install(root):
    site_manager = zope.component.getSiteManager()
    installLocalUtility(
        root, zeit.cms.repository.repository.repositoryFactory,
        'repository', zeit.cms.repository.interfaces.IRepository)
    installLocalUtility(
        root, zeit.cms.workingcopy.workingcopy.WorkingcopyLocation,
        'workingcopy', zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
    installLocalUtility(
        root, zeit.cms.content.template.TemplateManagerContainer,
        'templates', zeit.cms.content.interfaces.ITemplateManagerContainer)
    installTaskService()


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
