# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.cms.tagging.interfaces
import zeit.cms.tagging.whitelist


def update(root):
    zeit.cms.generation.install.installLocalUtility(
        root, zeit.cms.tagging.whitelist.Whitelist,
        'tag-whitelist', zeit.cms.tagging.interfaces.IWhitelist)


def evolve(context):
    zeit.cms.generation.do_evolve(context, update)
