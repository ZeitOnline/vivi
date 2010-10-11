# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.article.i18n import MessageFactory as _
import zeit.edit.interfaces
import zope.schema


class IEditableBody(zeit.edit.interfaces.IContainer):
  pass
