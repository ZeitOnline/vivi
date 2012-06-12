# Copyright (c) 2008-2012 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.objectlog.i18n import MessageFactory as _
import zeit.objectlog.source
import zope.app.security.vocabulary
import zope.configuration.fields
import zope.interface
import zope.schema


class IObjectLog(zope.interface.Interface):
    """Utility which logs object changes."""

    def log(object, message, mapping=None, timestamp=None):
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
        title=u'Arbitrary data to stroge along the log.',
        readonly=True,
        required=False)

    time = zope.schema.Datetime(
        title=u'Timestamp',
        readonly=True)

    def get_object():
        """return the affected object."""


class ILog(zope.interface.Interface):
    """Logging interface for one object."""

    def log(message, mapping=None, timestamp=None):
        """Log message for context."""

    def get_log():
        """Return log entries for context.

        Oldest first.
        """

    logs = zope.schema.Tuple(
        title=_('Log'),
        value_type=zope.schema.Choice(
            source=zeit.objectlog.source.LogEntrySource()),
        readonly=True)


class  ILogProcessor(zope.interface.Interface):
    """Adapter that may be used to process the context's object log."""

    def __call__(log_entries):
        """Transform an iterable of log entries into another."""
