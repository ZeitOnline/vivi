# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

from zeit.seo.i18n import MessageFactory as _

class ISEO(zope.interface.Interface):

    html_title = zope.schema.TextLine(
        title=_('HTML title'),
        required=False)

    html_description = zope.schema.Text(
        title=_('HTML description'),
        required=False)

    lexical_resource_query = zope.schema.TextLine(
        title=_('Lexical resource query'),
        required=False)

    left_column = zope.schema.Choice(
        title=_('Left column'),
        values=('custom',),
        required=False)
