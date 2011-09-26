# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.brightcove.repository


def install(root):
    # empty install just to have one because it makes live easier later on.
    pass

def evolve(context):
    zeit.cms.generation.do_evolve(context, install)

