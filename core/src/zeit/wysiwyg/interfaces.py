# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

import zc.form.field

from zeit.cms.i18n import MessageFactory as _

class IHTMLContent(zope.interface.Interface):

    html = zc.form.field.HTMLSnippet(title=_("Document"))
