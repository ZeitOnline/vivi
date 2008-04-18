# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.interface


class IObjectLog(zope.interface.Interface):
    """Utility which logs object changes."""

    def log(object, message_id, mapping):
        """Log message for object."""

    def get_log(object):
        """Return log entries for `object`.

        Oldest first.
        """

class ILogEntry(zope.interface.Interface):
    """One entry in the log."""

    principal = zope.schema.Choice(
        title=u'Principal',
        required=False,
        readonly=True,
        source=zope.app.security.vocabulary.PrincipalSource())

    message = zope.configuration.fields.MessageID(
        title=u'Log message',
        readonly=True)

    mapping = zope.schema.Dict(
        title=u'Mapping to replace variables in message',
        readonly=True,
        required=False)

    def get_object():
        """return the affected object."""
