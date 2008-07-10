# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import lovely.removetask.processor

import zeit.cms.generation


def update(root):
    # Use MultiProcessor for parallel processing.
    tasks = root.getSiteManager()['tasks.general']
    tasks.processorFactory = lovely.remotetask.processor.MultiProcessor


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
