from uuid import uuid4
import logging

from sqlalchemy import delete, select
import grokcore.component as grok
import zope.component
import zope.interface
import zope.security.management

from zeit.cms.i18n import MessageFactory as _
from zeit.connector import models
from zeit.workflow.scheduled.interfaces import IScheduledOperation, IScheduledOperations
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zeit.connector.interfaces
import zeit.objectlog.interfaces


log = logging.getLogger(__name__)


@grok.implementer(IScheduledOperation)
class ScheduledOperation:
    """Read-only view of a scheduled operation."""

    def __init__(self, model):
        self._model = model

    @property
    def id(self):
        return self._model.id

    @property
    def operation(self):
        return self._model.operation

    @property
    def scheduled_on(self):
        return self._model.scheduled_on

    @property
    def property_changes(self):
        return self._model.property_changes or {}

    @property
    def created_by(self):
        return self._model.created_by

    @property
    def date_created(self):
        return self._model.date_created


@grok.implementer(IScheduledOperations)
@grok.adapter(zeit.cms.interfaces.ICMSContent)
class ScheduledOperations:
    def __init__(self, context):
        self.context = context

    def add(self, operation, scheduled_on, property_changes=None):
        if operation not in ('publish', 'retract'):
            raise ValueError(f'Invalid operation: {operation}')

        if property_changes:
            self._validate_property_changes(property_changes)

        content_id = zeit.cms.content.interfaces.IUUID(self.context).shortened
        model = models.ScheduledOperation(
            id=str(uuid4()),
            content=content_id,
            operation=operation,
            scheduled_on=scheduled_on,
            property_changes=property_changes or {},
            created_by=self._get_principal(),
        )

        self._connector.session.add(model)

        log_util = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log_util.log(
            self.context,
            _(
                'Scheduled ${op} for ${date}',
                mapping={'op': operation, 'date': scheduled_on.isoformat()},
            ),
        )

        return model.id

    def remove(self, operation_id):
        try:
            result = self._connector.session.execute(
                delete(models.ScheduledOperation).where(
                    models.ScheduledOperation.id == operation_id
                )
            )

            if result.rowcount == 0:
                raise KeyError(f'Operation {operation_id} not found')
        except Exception as e:
            # XXX add raise from
            if 'invalid input syntax' in str(e):
                raise KeyError(f'Operation {operation_id} not found')
            raise

    def update(self, operation_id, scheduled_on=None, property_changes=None):
        model = self._get_stored_operation(operation_id)

        if scheduled_on is not None:
            model.scheduled_on = scheduled_on

        if property_changes is not None:
            self._validate_property_changes(property_changes)
            model.property_changes = property_changes

    def list(self, operation=None):
        content_id = zeit.cms.content.interfaces.IUUID(self.context).shortened
        if not content_id:
            return []

        query = select(models.ScheduledOperation).where(
            models.ScheduledOperation.content == content_id
        )

        if operation:
            query = query.where(models.ScheduledOperation.operation == operation)

        query = query.order_by(models.ScheduledOperation.scheduled_on)

        results = self._connector.session.execute(query).scalars()
        return [ScheduledOperation(model) for model in results]

    def get(self, operation_id):
        model = self._get_stored_operation(operation_id)
        return ScheduledOperation(model)

    @property
    def _connector(self):
        return zope.component.getUtility(zeit.connector.interfaces.IConnector)

    def _get_stored_operation(self, operation_id):
        try:
            model = self._connector.session.get(models.ScheduledOperation, operation_id)
            if not model:
                raise KeyError(f'Operation {operation_id} not found')
            return model
        except Exception as e:
            # Catch SQL errors (e.g., invalid UUID format) and convert to KeyError
            if 'invalid input syntax' in str(e):
                raise KeyError(f'Operation {operation_id} not found')
            raise

    def _validate_property_changes(self, property_changes):
        """Validate property changes reference valid properties."""
        if not isinstance(property_changes, dict):
            raise ValueError('property_changes must be a dict')

        if not property_changes:
            return

        for prop_name in property_changes:
            if not isinstance(prop_name, str):
                raise ValueError(f'Property name must be string, got {type(prop_name)}')

            if not hasattr(self.context, prop_name):
                log.warning(
                    'Property %s not found on %s, validation skipped',
                    prop_name,
                    self.context.uniqueId,
                )

    def _get_principal(self):
        """In case of multiple principals we take the first one we can get"""
        interaction = zope.security.management.getInteraction()
        if interaction and interaction.participations:
            return interaction.participations[0].principal.id
        return None
