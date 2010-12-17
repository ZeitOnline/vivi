# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt
import zope.deferredimport

zope.deferredimport.define(
    product_config='zeit.workflow.testing:product_config',
    WorkflowScriptsLayer='zeit.workflow.testing:WorkflowScriptsLayer')

