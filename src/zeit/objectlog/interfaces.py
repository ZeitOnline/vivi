# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface

from zeit.cms.i18n import MessageFactory as _


class IObjectLog(zope.interface.Interface):
    """Utility which logs object changes."""

    def log(object, field, old_value, new_value):
        pass

    def get_log(object):
        """Return log entries for `object`."""



class ILogEntry(zope.interface.Interface):
    """One entry in the log."""

    principal = zope.schema.Choice(
        title=_('Principal')
        required=False,
        readonly=True,
        source=zope.app.security.vocabulary.PrincipalSource())

    object = zope.schema.Object(
        zope.interface.Interface,
        title=_("Affected object."))

    #title
    #name
    #old_value
    #new_value



