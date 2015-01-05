# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation


def install(root):
    return  # Used to install teasergroup repository, which has been removed.


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
