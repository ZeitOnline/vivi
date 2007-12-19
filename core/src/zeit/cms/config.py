# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

# XXX remove thos module ASAP

import os.path

import zope.app.appsetup.product


cms_config = zope.app.appsetup.product.getProductConfiguration(
    'zeit.cms')
if cms_config is None:
    raise RuntimeError("config was imported too early")
