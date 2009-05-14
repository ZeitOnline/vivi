# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.blocks
import zeit.content.cp.testing


def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'teaser.txt',
        'cpextra.txt',
        'xml.txt')
