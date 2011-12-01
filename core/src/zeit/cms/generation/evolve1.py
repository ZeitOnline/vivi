# Copyright (c) 2008-2011 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zeit.cms.generation
import zeit.cms.generation.install


def update(root):
    zeit.cms.generation.install.installGeneralTaskService()


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
