# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.content.cp.teasergroup.interfaces
import zeit.content.cp.teasergroup.teasergroup


def install(root):
    zeit.cms.generation.install.installLocalUtility(
        root,
        zeit.content.cp.teasergroup.teasergroup.Repository,
        u'repository-teasergroups',
        zeit.content.cp.teasergroup.interfaces.IRepository)



def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
