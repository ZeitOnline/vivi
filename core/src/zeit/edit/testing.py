# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


EditLayer = zeit.cms.testing.ZCMLLayer('ftesting.zcml')


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = EditLayer
