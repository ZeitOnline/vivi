# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install
import zeit.vgwort.interfaces
import zeit.vgwort.token


def install(root):
    zeit.cms.generation.install.installLocalUtility(
        root, zeit.vgwort.token.TokenStorage, 'vgwort-tokens',
        zeit.vgwort.interfaces.ITokens)


def evolve(context):
    zeit.cms.generation.do_evolve(context, install)
