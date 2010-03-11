# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.content.tests.test_contentsource
import zeit.content.cp.testing
import zeit.content.cp.interfaces


class CPSourceTest(
    zeit.cms.content.tests.test_contentsource.ContentSourceTest):

    layer = zeit.content.cp.testing.layer

    source = zeit.content.cp.interfaces.centerPageSource
    expected_types = ['centerpage-2009']
