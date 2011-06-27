# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


zcml_layer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class TestCase(zeit.cms.testing.FunctionalTestCase):

    layer = zcml_layer
