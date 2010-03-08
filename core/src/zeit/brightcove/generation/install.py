# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.brightcove.repository


def install(root):
    zeit.cms.generation.install.installLocalUtility(
        root,
        zeit.brightcove.repository.Repository,
        u'repository-brightcove',
        zeit.brightcove.interfaces.IRepository)


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
