from collections.abc import Iterable
from datetime import datetime

import zope.interface
import zope.schema

from zeit.cms.i18n import MessageFactory as _


class IScheduledOperation(zope.interface.Interface):
    """A single scheduled operation."""

    id = zope.schema.TextLine(title=_('Operation ID'), readonly=True)
    operation = zope.schema.Choice(
        title=_('Operation type'), values=('publish', 'retract'), required=True
    )
    scheduled_on = zope.schema.Datetime(title=_('Execute at'), required=True)
    property_changes = zope.schema.Dict(
        title=_('Property changes (applied during operation)'),
        key_type=zope.schema.TextLine(),
        value_type=zope.schema.Field(),
        required=False,
    )
    created_by = zope.schema.TextLine(title=_('Created by'), readonly=True)
    date_created = zope.schema.Datetime(title=_('Date created'), readonly=True)
    executed_on = zope.schema.Datetime(
        title=_('Date executed or cancelled'),
        description=_('When the operation was executed or cancelled. NULL means still pending.'),
        required=False,
        readonly=True,
    )


class IScheduledOperations(zope.interface.Interface):
    """Manage scheduled operations for content."""

    def add(operation: str, scheduled_on: datetime, property_changes: dict | None = None) -> str:
        """Schedule an operation.

        operation: 'publish' or 'retract'
        scheduled_on: datetime when to execute
        property_changes: dict of properties to change

        returns operation_id (str): UUID of created operation
        """

    def remove(operation_id: str):
        """Cancel a scheduled operation.

        raises KeyError if operation_id not found
        """

    def update(
        operation_id: str,
        scheduled_on: datetime | None = None,
        executed_on: datetime | None = None,
        property_changes: dict | None = None,
    ):
        """Modify an existing operation.

        Only specified parameters are updated.

        raises KeyError if operation_id not found
        """

    def list(operation: str | None = None) -> list[IScheduledOperation]:
        """Return scheduled operations.

        operation: Filter by type ('publish' or 'retract'), or None for all

        returns List of IScheduledOperation objects, sorted by scheduled_on
        """

    def get(operation_id: str) -> IScheduledOperation:
        """Get a specific operation by ID.

        raises KeyError if operation_id not found
        """

    def synchronize(operations: Iterable[IScheduledOperation]):
        """Replace all operations with the given list (bulk delete + bulk insert).

        More efficient than individual synchronize calls for large batches.
        """

    def execute(operation: IScheduledOperation):
        """Execute a single scheduled operation.

        raises ValueError if operation type is unknown
        """
