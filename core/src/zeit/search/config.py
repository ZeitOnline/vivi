# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os.path

import zope.app.appsetup.product


search_config = zope.app.appsetup.product.getProductConfiguration('zeit.search')

if search_config is None:
    XAPIAN_URL = 'file://%s' % (
        os.path.join(os.path.dirname(__file__),
                     'xapian-test.xml'))
else:
    XAPIAN_URL = search_config.get('xapian-url')
