from datetime import datetime
from typing import Any

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


class IScheduledOperations(zope.interface.Interface):
    """Manage scheduled operations for content."""

    def add(operation: str, scheduled_on: datetime, property_changes: dict | None = None) -> str:
        """Schedule an operation.

        operation: 'publish' or 'retract'
        scheduled_on: datetime when to execute
        property_changes: dict of properties to change

        returns operation_id (str): UUID of created operation
        raises ValueError if operation or property_changes invalid
        """

    def remove(operation_id: str):
        """Cancel a scheduled operation.

        raises KeyError if operation_id not found
        """

    def update(
        operation_id: str,
        scheduled_on: datetime | None = None,
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


class IScheduledOperationsStorage(zope.interface.Interface):
    """Storage backend for scheduled operations.

    This interface abstracts the persistence layer.
    """

    def add(
        operation_id: str,
        operation: str,
        scheduled_on: datetime,
        property_changes: dict | None,
        created_by: str | None,
        date_created: datetime | None = None,
    ):
        """Add a new scheduled operation to storage."""

    def remove(operation_id: str):
        """Remove operation from storage.

        Raises KeyError if operation_id not found.
        """

    def update(
        operation_id: str,
        scheduled_on: datetime | None = None,
        property_changes: dict | None = None,
    ):
        """Update operation in storage.

        Only updates fields that are not None.
        Raises KeyError if operation_id not found.
        """

    def list(operation: str | None = None) -> list[Any]:
        """List all operations for this content, optionally filtered by operation type."""

    def get(operation_id: str) -> Any:
        """Get single operation from storage.

        Returns storage-specific operation object.
        Raises KeyError if operation_id not found.
        """
