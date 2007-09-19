# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.appsetup.product


search_config = zope.app.appsetup.product.getProductConfiguration('zeit.search')

if search_config is None:
    XAPIAN_URL = 'XXX'
else:
    XAPIAN_URL = search_config.get('xapian-url')
