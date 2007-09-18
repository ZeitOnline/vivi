# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os

import zope.app.appsetup.product


cms_config = zope.app.appsetup.product.getProductConfiguration('zeit.cms')


if cms_config is None:
    # Test configuration
    base_path = os.path.dirname(__file__)

    SERIE_URL = 'file://%s' % os.path.join(base_path, 'content', 'serie.xml')
    RESSORT_URL = 'file://%s' % os.path.join(base_path, 'content', 'ressort.xml')
    PRINT_RESSORT_URL = 'file://%s' % os.path.join(
        base_path, 'content', 'ressort.xml')

else:

    SERIE_URL = cms_config.get('source-serie')
    RESSORT_URL = cms_config.get('source-ressort')
    PRINT_RESSORT_URL = cms_config.get('source-print-ressort')
