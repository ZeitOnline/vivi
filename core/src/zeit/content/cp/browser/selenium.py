# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.selenium


class TestGenericEditing(zeit.cms.selenium.Test):

    def test_foo(self):
        s = self.selenium
        self.open('/repository')
