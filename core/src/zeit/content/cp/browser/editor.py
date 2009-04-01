# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component
import zope.viewlet.interfaces
import zope.viewlet.viewlet
from zeit.content.cp.i18n import MessageFactory as _


class Editor(object):

    title = _('Edit center page')
