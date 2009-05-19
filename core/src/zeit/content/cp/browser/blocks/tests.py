# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks
import zeit.content.cp.testing

def test_suite():
    return zeit.content.cp.testing.FunctionalDocFileSuite(
        'av.txt',
        'cpextra.txt',
        'placeholder.txt',
        'quiz.txt',
        'rss.txt',
        'teaser.txt',
        'teaserbar.txt',
        'xml.txt',
        )
