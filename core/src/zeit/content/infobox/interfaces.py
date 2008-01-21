# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface
import zope.schema

import zc.form.field

from zeit.cms.i18n import MessageFactory as _


class IInfobox(zope.interface.Interface):

    supertitle = zope.schema.TextLine(title=_('Supertitle'))

    content = zope.schema.Tuple(
        title=_('Contents'),
        value_type=zc.form.field.Combination(
            (zope.schema.TextLine(
                title=_('Title')),
             zope.schema.Text(
                 title=_('Text')),
            )))

