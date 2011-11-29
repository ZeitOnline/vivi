# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install


def update(root):
    zeit.cms.generation.install.installLowPriorityTaskService()


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
