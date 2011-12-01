# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.content.article.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'edit.landing.txt',
        'edit.txt',
        'edit.related.txt',
        'edit.form.txt',
        package='zeit.content.article.edit.browser',
        layer=zeit.content.article.testing.ArticleLayer)
